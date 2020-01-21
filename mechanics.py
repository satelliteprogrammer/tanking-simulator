from __future__ import annotations
from abilities import Ability
from attr import attrs, attrib
from bisect import insort
from collections import deque, namedtuple
from encounter import Fight
from heals import Heal
from units import Boss, Healer, Tank
from typing import Deque, Dict, List
import random


@attrs(slots=True, eq=False)
class TimeEvent:
    time = attrib(type=float)
    event = attrib(type=object)

    def next(self, fight: Fight, trigger: TimeEvent = None) -> None:
        pass

    def __lt__(self, other):
        return self.time < other.time


@attrs(slots=True, eq=False)
class BossAttackEvent(TimeEvent):

    def next(self, fight: Fight, trigger: TimeEvent = None) -> None:
        boss = self.event

        roll = random.uniform(0, 100)
        if roll < fight.tank.stats.miss:
            fight.stats.miss()
        elif (roll := roll - fight.tank.stats.miss) < fight.tank.stats.dodge:
            fight.stats.dodge()
        elif (roll := roll - fight.tank.stats.dodge) < fight.tank.stats.parry:
            fight.stats.parry()
        elif (roll := roll - fight.tank.stats.parry) < fight.tank.stats.block:
            fight.stats.block()
            damage = ((1 - fight.tank.get_armor_reduction(fight.boss.level)) *
                      (boss.attack() - fight.tank.get_block_reduction()))
            fight.tank_hp.damage(damage, fight.current_time)
        elif (roll - fight.tank.stats.block) < 15:
            fight.stats.crush()
            damage = (1 - fight.tank.get_armor_reduction(fight.boss.level)) * boss.attack() * 1.5
            fight.tank_hp.damage(damage, fight.current_time)
        else:
            fight.stats.hit()
            damage = (1 - fight.tank.get_armor_reduction(fight.boss.level)) * boss.attack()
            fight.tank_hp.damage(damage, fight.current_time)

        self.time += boss.speed
        fight.queue.add(self)


@attrs(slots=True, eq=False)
class BossAbilityEvent(TimeEvent):

    def next(self, fight: Fight, trigger: TimeEvent = None) -> None:
        pass


@attrs(slots=True, eq=False)
class HealEvent(TimeEvent):

    def next(self, fight: Fight, trigger: TimeEvent = None) -> None:
        heal = self.event
        fight.tank_hp.heal(heal.apply(), fight.current_time)


@attrs(slots=True, eq=False)
class HealerEvent(TimeEvent):

    def next(self, fight: Fight, trigger: TimeEvent = None) -> None:
        healer = self.event

        if isinstance(trigger, BossAbilityEvent):
            HealerEvent.cancel_cast(fight, healer)
            self.time += self.move(fight)
            fight.queue.add(self)

        else:
            heal = healer.decision(fight.tank_hp)
            self.time += heal.cast
            heal_event = HealEvent(self.time, heal)
            fight.queue.add(heal_event)
            fight.queue.add(self)

    @staticmethod
    def cancel_cast(fight: Fight, healer: Healer):
        fight.queue.cancel(healer.current_cast())

    @staticmethod
    def move(fight: Fight) -> int:
        return fight.queue.last_ability.movement()


@attrs(slots=True, eq=False)
class HoTEvent(Hot, TimeEvent):

    def next(self, queue: Deque, trigger: TimeEvent = None) -> List[TimeEvent]:

        return


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

    def pop(self):
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