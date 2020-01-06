from dataclasses import dataclass
from enum import Enum
import types


@dataclass
class TimeEvent:
    __slots__ = 'time', 'event'
    time: float
    event: types.FunctionType

    def __repr__(self):
        s = 'TimeEvent {}s -> {}'.format(self.time, self.event.__name__)
        return s


@dataclass(eq=False)
class Stats:
    __slots__ = 'stamina', 'agility', 'strength', 'defense', 'miss', 'dodge', 'parry', 'block', 'block_value', 'armor',\
                'hit', 'expertise'

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


class TankHP:
    __slots__ = 'max', '__hp'

    def __init__(self, hp):
        self.max = hp
        self.__hp = [(0.0, hp)]

    def damage(self, damage: int, time: float):
        self.__hp.append((time, max(self.__hp[-1][1] - damage, 0)))

    def heal(self, heal: int, time: float):
        if self.max == self.__hp[-1][1]:
            return
        self.__hp.append((time, min(self.__hp[-1][1] + heal, self.max)))

    def get_hp(self):
        return self.__hp[-1][1]

    def get_fight(self):
        return self.__hp


class Statistics:
    def __init__(self):
        self.missed = self.dodged = self.parried = self.blocked = self.crushed = self.hitted = 0
        self.critical_events = 0
        self.hp = list()


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
