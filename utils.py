from __future__ import annotations
from attr import attrs, attrib, Factory
from bisect import insort
from collections import deque
from enum import Enum
from typing import Deque, Dict, List, Tuple


@attrs(slots=True, auto_attribs=True)
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
    hit: float
    expertise: float
    hp: float


@attrs(slots=True, auto_attribs=True, init=False)
class TankHP:
    full: int
    _hp: List[Tuple]

    def __init__(self, hp):
        self.full = hp
        self._hp = [(0.0, hp)]

    def damage(self, damage: int, time: float):
        self._hp.append((time, max(self.get_hp() - damage, 0)))

    def heal(self, heal: int, time: float) -> int:
        """ :returns effective heal"""

        if (hp := self.get_hp() + heal) < self.full:
            self._hp.append((time, hp))
            return heal
        else:
            self._hp.append((time, self.full))
            return heal - hp + self.full

    def get_hp(self):
        return self._hp[-1][1]

    def get_fight(self):
        return self._hp


@attrs(slots=True)
class Statistics:
    _missed = attrib(init=False, default=0, type=int)
    _dodged = attrib(init=False, default=0, type=int)
    _parried = attrib(init=False, default=0, type=int)
    _blocked = attrib(init=False, default=0, type=int)
    _crushed = attrib(init=False, default=0, type=int)
    _hitted = attrib(init=False, default=0, type=int)
    _critical_events = attrib(init=False, default=0, type=int)
    _hp = attrib(init=False, default=None, type=TankHP)

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
