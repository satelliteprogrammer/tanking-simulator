from __future__ import annotations
from abilities import Ability
from attr import attrs, attrib
from bisect import insort
from collections import deque, namedtuple
from heals import Heal
from units import Boss, Healer, Tank
from utils import FightOver, Order, Statistics, TankHP
from typing import Deque, Dict, List
import random


@attrs(slots=True, eq=False)
class TimeEvent:
    time = attrib(type=float)

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> None:
        pass

    def __lt__(self, other):
        return self.time < other.time


@attrs(slots=True, eq=False)
class BossEvent(TimeEvent):

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> None:

        roll = random.uniform(0, 100)
        if roll < fight.tank.attributes.miss:
            fight.stats.miss()
        elif (roll := roll - fight.tank.attributes.miss) < fight.tank.attributes.dodge:
            fight.stats.dodge()
        elif (roll := roll - fight.tank.attributes.dodge) < fight.tank.attributes.parry:
            fight.stats.parry()
        elif (roll := roll - fight.tank.attributes.parry) < fight.tank.attributes.block:
            fight.stats.block()
            damage = ((1 - fight.tank.get_armor_reduction(fight.boss.level)) *
                      (fight.boss.attack() - fight.tank.get_block_reduction()))
            fight.tank_hp.damage(damage, fight.current_time)
        elif (roll - fight.tank.attributes.block) < 15:
            fight.stats.crush()
            damage = (1 - fight.tank.get_armor_reduction(fight.boss.level)) * fight.boss.attack() * 1.5
            fight.tank_hp.damage(damage, fight.current_time)
        else:
            fight.stats.hit()
            damage = (1 - fight.tank.get_armor_reduction(fight.boss.level)) * fight.boss.attack()
            fight.tank_hp.damage(damage, fight.current_time)

        self.time += fight.boss.speed
        fight.queue.add(self)


@attrs(slots=True, eq=False)
class BossAbilityEvent(TimeEvent):

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> None:
        pass


@attrs(slots=True, eq=False)
class HealEvent(TimeEvent):
    heal = attrib(type=Heal)

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> None:
        fight.tank_hp.heal(self.heal.apply(), fight.current_time)


@attrs(slots=True, eq=False)
class HoTEvent(TimeEvent):
    heal = attrib(type=Heal)

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> None:
        pass


@attrs(slots=True, eq=False)
class HealerEvent(TimeEvent):
    healer = attrib(type=Healer)

    def __call__(self, fight: Fight, trigger: TimeEvent = None) -> None:

        if isinstance(trigger, BossAbilityEvent):
            HealerEvent.cancel_cast(fight, self.healer)
            self.time += self.move(fight)
            fight.queue.add(self)

        else:
            heal = self.healer.decision(fight.tank_hp)
            self.time += heal.cast_time
            heal_event = HealEvent(time=self.time, heal=heal)
            fight.queue.add(heal_event)
            fight.queue.add(self)

    @staticmethod
    def cancel_cast(fight: Fight, healer: Healer):
        fight.queue.cancel(healer.current_cast())

    @staticmethod
    def move(fight: Fight) -> int:
        return fight.queue.last_ability.movement()


@attrs(slots=True)
class Queue:
    queue = attrib(default=deque(), type=Deque)
    dict = attrib(default=dict(), type=Dict)
    last_ability = attrib(default=None, type=BossAbilityEvent)

    def add(self, te: TimeEvent):
        if te in self.dict:
            raise AttributeError
        else:
            self.dict[te] = te.time
            insort(self.queue, te)

    def next(self):
        try:
            while not (next := self.queue.popleft()) in self.dict:
                pass
        except IndexError:
            return None

        del self.dict[next]
        if isinstance(next, BossAbilityEvent):
            self.last_ability = next

        return next

    def cancel(self, e):
        del self.dict[e]

    def next_time(self):
        return self.queue[0].time


class Fight:

    def __init__(self, boss: Boss, tank: Tank, healer: Healer, duration,
                 events: Queue = Queue(), order: Order = Order.RANDOM):
        self.boss = boss
        self.tank = tank
        self.healer = healer
        self.duration = duration
        self.order = order

        self.tank_hp = TankHP(tank.hp)

        self.stats = Statistics()
        self.stats.set_tank_hp(self.tank_hp)

        self.current_time = 0
        self.queue = events

    def initialize(self):
        self.queue.add(BossEvent(0))
        self.queue.add(HealerEvent(0, self.healer))

    def finish(self) -> (Statistics, int):
        return self.stats, self.current_time

    def next(self) -> None:
        e = self.queue.next()

        self.current_time = e.time

        if self.current_time > self.duration:
            raise FightOver

        # current_events = dict()
        # current_events[str(e[1].__name__)] = e
        if self.queue.next_time() == self.current_time:
            self.stats.critical_event()
            # e = self.events.popleft()
            # current_events[str(e[1].__name__)] = e

        e(self)

        if self.tank_hp.get_hp() == 0:
            raise FightOver
