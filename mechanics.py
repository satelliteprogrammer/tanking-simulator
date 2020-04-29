from __future__ import annotations
from abilities import Ability
from attr import attrs, attrib, Factory
from bisect import insort
from collections import deque, namedtuple
from heals import Heal, HoT, LB, REG, REGHoT
from healers import Healer
from units import Boss, Tank
from utils import FightOver, Order, Statistics, TankHP
from typing import Deque, Dict, List, TypeVar, Tuple
import random


@attrs(slots=True, eq=False)
class TimeEvent:
    time = attrib(type=float)

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> List:
        pass

    def __lt__(self, other):
        return self.time < other.time


@attrs(slots=True, eq=False, repr=False)
class HealEvent(TimeEvent):
    heal = attrib(type=Heal)
    last_heal = attrib(type=Tuple, default=())

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> List:
        if heal := self.heal.apply():
            effective_heal = fight.tank_hp.heal(heal, fight.current_time)
            self.last_heal = (self.time, heal, effective_heal)

        if next_heal := self.heal.next():
            if isinstance(self.heal, REG) and (regrowth := fight.queue.get_hot_event(REGHoT)):
                # FUCK regrowth
                fight.queue.remove(regrowth)

            if isinstance(next_heal, HoT):
                next_time = self.time + next_heal._tick_period
            else:
                next_time = self.time
            return [HealEvent(time=next_time, heal=next_heal)]

        return []

    def __repr__(self):
        if not self.last_heal:
            return ''
        return f'<{self.last_heal[0]:.2f}> {self.heal._name} heals for {self.last_heal[2]} ({self.last_heal[1]})'


@attrs(slots=True, eq=False, repr=False)
class HealerEvent(TimeEvent):
    healer = attrib(type=Healer)
    casting = attrib(type=Heal, default=None)
    decision = attrib(type=Tuple, default=())

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> List:
        next_events = [self]

        if isinstance(trigger, BossAbilityEvent):
            self.cancel_cast()
            self.decision = (self.time, 'cancel cast')
            self.time += self.move(fight)
            return [self]

        else:
            if self.casting:
                # TODO add check spell finish
                if isinstance(self.casting, HoT):
                    if hot_event := fight.queue.get_hot_event(self.casting):
                        fight.queue.remove(hot_event)
                    next_events.append(HealEvent(time=self.time+self.casting.tick_period, heal=self.casting))
                else:
                    next_events.append(HealEvent(time=self.time, heal=self.casting))
                self.casting = None

            if self.healer.latency:
                self.time += self.healer.latency

            next_heal = self.healer.decision(self.time, fight.tank_hp)

            if next_heal:
                self.decision = (self.time, next_heal)

                if next_heal.cast_time:
                    self.casting = next_heal
                    self.time += self.casting.cast_time

                else:
                    if isinstance(next_heal, HoT):
                        if hot_event := fight.queue.get_hot_event(next_heal):
                            if isinstance(lb := hot_event.heal, LB):
                                lb.healer = next_heal.healer
                                lb.reapply()
                            else:
                                fight.queue.remove(hot_event)
                                next_events.append(HealEvent(time=self.time+next_heal._tick_period, heal=next_heal))
                        else:
                            next_events.append(HealEvent(time=self.time + next_heal._tick_period, heal=next_heal))
                    self.time += self.healer.gcd()

            else:
                self.time += self.healer.gcd()
                self.decision = (self.time, 'nothing')

            return next_events

    def cancel_cast(self):
        self.casting = None

    @staticmethod
    def move(fight: Fight) -> int:
        return fight.queue.last_ability.movement()

    def __repr__(self):
        return f'<{self.decision[0]:.2f}> {self.healer.name} casts {self.decision[1]}'


@attrs(slots=True, eq=False)
class AttackEvent(TimeEvent):
    unit = attrib()

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> List[AttackEvent]:
        pass


@attrs(slots=True, eq=False, repr=False)
class BossAttackEvent(AttackEvent):
    unit = attrib(type=Boss)
    last_attack = attrib(type=Tuple, default=())

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> List[BossAttackEvent]:
        next_events = [self]

        roll = random.uniform(0, 100)
        if roll < fight.tank.attributes.miss:
            fight.stats.miss()
            damage = 0
            self.last_attack = (self.time, 'missed')
        elif (roll := roll - fight.tank.attributes.miss) < fight.tank.attributes.dodge:
            fight.stats.dodge()
            damage = 0
            self.last_attack = (self.time, 'dodged')
        elif (roll := roll - fight.tank.attributes.dodge) < fight.tank.attributes.parry:
            fight.stats.parry()
            damage = 0
            self.last_attack = (self.time, 'parried')
        elif (roll := roll - fight.tank.attributes.parry) < fight.tank.attributes.block:
            fight.stats.block()
            self.last_attack = (self.time, 'blocked')
            damage = ((1 - fight.tank.get_armor_reduction(fight.boss.level)) *
                      (fight.boss.attack() - fight.tank.get_block_reduction()))
        elif (roll - fight.tank.attributes.block) < 15:
            fight.stats.crush()
            damage = (1 - fight.tank.get_armor_reduction(fight.boss.level)) * fight.boss.attack() * 1.5
            self.last_attack = (self.time, 'crushed')
        else:
            fight.stats.hit()
            damage = (1 - fight.tank.get_armor_reduction(fight.boss.level)) * fight.boss.attack()
            self.last_attack = (self.time, 'hitted')

        if damage:
            next_events.extend([HealEvent(time=self.time, heal=heal) for heal in fight.reactive_heals])

        fight.tank_hp.damage(damage, fight.current_time)
        self.time += fight.boss.weapon_speed
        return next_events

    def __repr__(self):
        return f'<{self.last_attack[0]:.2f}> {self.unit.name} {self.last_attack[1]}'


@attrs(slots=True, eq=False)
class BossAbilityEvent(TimeEvent):
    unit = attrib(type=Boss)

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> List:
        pass


@attrs(slots=True, eq=False, repr=False)
class TankAttackEvent(AttackEvent):
    unit = attrib(type=Tank)
    parry_hasted = attrib(type=Tuple, default=())

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> List[TankAttackEvent]:
        roll = random.uniform(0, 100)
        if roll < max(9 - fight.tank.attributes.hit, 0):
            pass
        elif (roll := roll - max(9 - fight.tank.attributes.hit, 0)) < max(6.5 - fight.tank.attributes.expertise * .25, 0):
            pass
        elif (roll := roll - max(6.5 - fight.tank.attributes.expertise * .25, 0)) < max(16 - fight.tank.attributes.expertise * .25, 0):
            # parry haste
            fight.queue.parry_haste(self.time, BossAttackEvent)
            self.parry_hasted = (self.time, )
        else:
            pass

        self.time += fight.tank.weapon_speed
        return [self]

    def __repr__(self):
        if not self.parry_hasted:
            return ''
        ret = f'<{self.parry_hasted[0]:.2f}> I got parried'
        self.parry_hasted = ()
        return ret


@attrs(slots=True)
class Queue:
    queue = attrib(default=Factory(deque), type=Deque)
    dictionary = attrib(default=Factory(dict), type=Dict)
    last_ability = attrib(default=None, type=BossAbilityEvent)
    history = attrib(default=Factory(list), type=List)

    # def __init__(self, queue=None, dictionary=None, last_ability=None, history=None):
    #     if not queue:
    #         self.queue = deque()
    #     else:
    #         self.queue = queue
    #     if not dictionary:
    #         self.dictionary = dict()
    #     else:
    #         self.dictionary = dictionary
    #     self.last_ability = last_ability
    #     if not history:
    #         self.history = list()
    #     else:
    #         self.history = history

    def add(self, lte: List):
        for te in lte:
            if te in self.dictionary:
                raise AttributeError
            else:
                self.dictionary[te] = te.time
                insort(self.queue, te)

    def next(self) -> TimeEvent:
        try:
            while not (next := self.queue.popleft()) in self.dictionary:
                pass
        except IndexError:
            raise FightOver('Queue had no more events...')

        del self.dictionary[next]
        if isinstance(next, BossAbilityEvent):
            self.last_ability = next

        return next

    def get_instance(self, event_type: TypeVar) -> TimeEvent:
        for e in self.queue:
            if isinstance(e, event_type):
                return e

    def cancel(self, event: TimeEvent):
        del self.dictionary[event]

    def remove(self, event: TimeEvent):
        self.queue.remove(event)
        self.cancel(event)

    def next_time(self):
        return self.queue[0].time

    def parry_haste(self, time: float, attack_type: TypeVar[AttackEvent]):
        next_attack = self.get_instance(attack_type)
        previous_attack = next_attack.time - next_attack.unit.weapon_speed

        if time > next_attack.time - next_attack.unit.weapon_speed * .2:
            pass
        else:
            new_attack = min(next_attack.time - next_attack.unit.weapon_speed * .2,
                             next_attack.time - next_attack.unit.weapon_speed * .4)

            self.remove(next_attack)
            next_attack.time = new_attack
            self.add([next_attack])

    def get_hot_event(self, hot: HoT):
        for e in reversed(self.queue):
            if isinstance(e, HealEvent) and e.heal == hot:
                return e


@attrs(slots=True)
class Fight:
    boss = attrib(type=Boss)
    tank = attrib(type=Tank)
    healers = attrib(type=List[Healer])
    duration = attrib(type=int)
    queue = attrib(default=Factory(Queue), type=Queue)
    order = attrib(default=Order.RANDOM, type=Order)
    tank_hp = attrib(init=False, type=TankHP)
    reactive_heals = attrib(init=False, default=list())
    current_time = attrib(init=False, default=0, type=float)
    stats = attrib(init=False, default=Factory(Statistics), type=Statistics)

    def __attrs_post_init__(self):
        self.tank_hp = TankHP(self.tank.attributes.hp)
        self.stats.set_tank_hp(self.tank_hp)

    def initialize(self) -> None:
        self.queue.add([BossAttackEvent(time=0, unit=self.boss)])
        self.queue.add([TankAttackEvent(time=0, unit=self.tank)])
        for healer in self.healers:
            # casting = healer.decision(self.tank_hp)
            self.queue.add([HealerEvent(time=-1, healer=healer)])
        # self.queue.add() TODO tank attacks

    def statistics(self) -> (Statistics, List):
        return self.stats, self.queue.history, self

    def run(self) -> None:
        while True:
            try:
                self.next()
            except FightOver:
                return

    def next(self) -> None:
        event = self.queue.next()

        self.current_time = event.time

        if self.current_time > self.duration:
            self.queue.history.append(f'Boss conquered!')
            raise FightOver

        # current_events = dict()
        # current_events[str(e[1].__name__)] = e
        if self.queue.next_time() == self.current_time:
            self.stats.critical_event()
            # e = self.events.popleft()
            # current_events[str(e[1].__name__)] = e

        next_event = event(self)

        # logging
        if hist := repr(event):
            self.queue.history.append(hist)

        if self.tank_hp.get_hp() <= 0:
            self.queue.history.append(f'Tank died!')
            raise FightOver

        if next_event:
            self.queue.add(next_event)
