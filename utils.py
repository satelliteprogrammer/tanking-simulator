from collections import deque
from dataclasses import dataclass
from enum import Enum
from mechanics import TimeEvent, BossAbilityEvent
from typing import Deque, Dict, List, Tuple
import attr
import bisect


@attr.s(slots=True, auto_attribs=True)
class Stats:
    stamina: float
    agility: float
    strength: float
    defense: float
    miss: float
    dodge: float
    parry: float
    block: float
    block_value: int
    armor: int
    hit: int
    expertise: int


@attr.s(slots=True)
class Queue:
    queue = attr.ib(default=deque(), type=Deque)
    dict = attr.ib(default=dict(), type=Dict)
    last_ability = attr.ib(default=None, type=BossAbilityEvent)

    def add(self, te: TimeEvent):
        if te in self.dict:
            raise AttributeError
        else:
            self.dict[te] = te.time
            bisect.insort(self.queue, te)

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


@attr.s(slots=True, auto_attribs=True, init=False)
class TankHP:
    max: int
    _hp: List[Tuple]

    def __init__(self, hp):
        self.max = hp
        self._hp = [(0.0, hp)]

    def damage(self, damage: int, time: float):
        self._hp.append((time, max(self._hp[-1][1] - damage, 0)))

    def heal(self, heal: int, time: float):
        if self.max == self._hp[-1][1]:
            return
        self._hp.append((time, min(self._hp[-1][1] + heal, self.max)))

    def get_hp(self):
        return self._hp[-1][1]

    def get_fight(self):
        return self._hp


@attr.s(slots=True)
class Statistics:
    _missed = attr.ib(default=0)
    _dodged = attr.ib(default=0)
    _parried = attr.ib(default=0)
    _blocked = attr.ib(default=0)
    _crushed = attr.ib(default=0)
    _hitted = attr.ib(default=0)
    _critical_events = attr.ib(default=0)
    _hp = attr.ib(default=attr.Factory(tuple))

    def miss(self):
        self._missed += 1

    def dodge(self):
        self._dodged += 1

    def parry(self):
        self._parried += 1

    def block(self):
        self._blocked += 1

    def crush(self):
        self._crushed += 1

    def hit(self):
        self._hitted += 1

    def critical_event(self):
        self._critical_events += 1

    def set_tank_hp(self, hp: TankHP):
        self._hp = hp

    def get_stats(self):
        return self._missed, self._dodged, self._parried, self._blocked, self._crushed, self._hitted

    def get_critical_events(self):
        return self._critical_events

    def get_tank_hp(self) -> TankHP:
        return self._hp


class Order(Enum):
    LENIENT = 0
    HARSH = 1
    RANDOM = 2


class FightOver(Exception):
    pass


def trange(stop):
    i = 0
    while i < stop:
        yield i
        i += 0.01
