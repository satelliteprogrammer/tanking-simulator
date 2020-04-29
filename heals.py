from attr import attrs, attrib
from math import floor
from random import random, uniform
from statistics import mean
from units import Healer
from typing import Tuple


@attrs(slots=True, repr=False, eq=False)
class Heal:
    _name = attrib(init=False, type=str)
    _base = attrib(init=False, type=Tuple[int, int])
    _coefficient = attrib(init=False, type=float)
    _healing_multiplier = attrib(init=False, default=0, type=float)
    _crit_multiplier = attrib(init=False, default=0, type=float)
    cast_time = attrib(init=False, type=float)
    healer = attrib(type=Healer)
    increased_healing = attrib(type=int, default=0)
    increased_haste = attrib(type=float, default=0)
    increased_crit = attrib(type=float, default=0)

    def __attrs_post_init__(self):
        self.cast_time = self.cast_time / (1 + self.healer.haste)
        self.increased_healing += self._healing_multiplier
        self.increased_crit += self._crit_multiplier

    def apply(self):
        base_heal = uniform(self._base[0], self._base[1])
        heal = (base_heal + self._coefficient * self.healer.bonus_healing) * (1 + self.increased_healing)

        if random() < (self.healer.crit + self.increased_crit):
            return floor(heal * 1.5)
        else:
            return floor(heal)

    def next(self):
        return None

    def hps(self):
        heal = (mean(self._base) + self._coefficient * self.healer.bonus_healing) * (1 + self.increased_healing)
        crit = self.healer.crit + self.increased_crit
        return (heal * 1.5 * crit + heal * (1 - crit))/self.cast_time

    def __eq__(self, other):
        if self._name == other._name and self.healer == other.healer:
            return True
        return False

    def __repr__(self):
        return f'{self._name}'


@attrs(slots=True, repr=False, eq=False)
class HoT(Heal):
    _base = attrib(init=False, type=int)
    _duration = attrib(init=False, type=int)
    _tick_period = attrib(init=False, type=int)
    _time_elapsed = attrib(init=False, default=0)
    _heal_per_tick = attrib(init=False, default=0)

    def __attrs_post_init__(self):
        self._heal_per_tick = self._duration/self._tick_period

    def apply(self):
        heal = (self._base + self._coefficient * self.healer.bonus_healing) * (1 + self.increased_healing)
        return floor(heal / self._heal_per_tick)

    def next(self):
        self._time_elapsed += self._tick_period
        if self._time_elapsed > self._duration:
            return None
        else:
            return self


@attrs(slots=True, repr=False, eq=False)
class HL11(Heal):
    _name = attrib(init=False, default='Holy Light (Rank 11)')
    _base = attrib(init=False, default=(2196, 2447))
    _coefficient = attrib(init=False, default=.714)
    _healing_multiplier = attrib(init=False, default=.12)
    _crit_multiplier = attrib(init=False, default=.11)
    cast_time = attrib(init=False, default=2)


@attrs(slots=True, repr=False, eq=False)
class HL9(Heal):
    _name = attrib(init=False, default='Holy Light (Rank 9)')
    _base = attrib(init=False, default=(1590, 1771))
    _coefficient = attrib(init=False, default=.714)
    _healing_multiplier = attrib(init=False, default=.12)
    _crit_multiplier = attrib(init=False, default=.11)
    cast_time = attrib(init=False, default=2)


@attrs(slots=True, repr=False, eq=False)
class FoL(Heal):
    _name = attrib(init=False, default='Flash of Light')
    _base = attrib(init=False, default=(448, 503))
    _coefficient = attrib(init=False, default=.429)
    _healing_multiplier = attrib(init=False, default=.12)
    _crit_multiplier = attrib(init=False, default=.06)
    cast_time = attrib(init=False, default=1.5)


@attrs(slots=True, repr=False, eq=False)
class REJ(HoT):
    _name = attrib(init=False, default='Rejuvenation')
    _base = attrib(init=False, default=1060)
    _coefficient = attrib(init=False, default=.8 * 1.2)
    _duration = attrib(init=False, default=12)
    _tick_period = attrib(init=False, default=3)
    _healing_multiplier = attrib(init=False, default=(1.1 * 1.15) - 1)
    cast_time = attrib(init=False, default=0)


@attrs(slots=True, repr=False, eq=False)
class LBBloom(Heal):
    _name = attrib(init=False, default='Lifebloom')
    _base = attrib(init=False, default=600)
    _coefficient = attrib(init=False, default=.3429 * 1.2)
    _healing_multiplier = attrib(init=False, default=0)
    _crit_multiplier = attrib(init=False, default=.03)
    cast_time = attrib(init=False, default=0)

    _stack = attrib(init=False, default=3)

    def apply(self):
        heal = (self._base + self._coefficient * self.healer.bonus_healing) * (1 + self.increased_healing) * self._stack

        if random() < (self.healer.crit + self.increased_crit):
            return floor(heal * 1.5)
        else:
            return floor(heal)


@attrs(slots=True, repr=False, eq=False)
class LB(HoT):
    _name = attrib(init=False, default='Lifebloom')
    _base = attrib(init=False, default=273)
    _coefficient = attrib(init=False, default=.5180 * 1.2)
    _duration = attrib(init=False, default=7)
    _tick_period = attrib(init=False, default=1)
    _healing_multiplier = attrib(init=False, default=.1)
    cast_time = attrib(init=False, default=0)

    _stack = attrib(init=False, default=1)

    def next(self):
        self._time_elapsed += self._tick_period
        if self._time_elapsed > self._duration:
            return LBBloom(healer=self.healer)
        else:
            return self

    def apply(self):
        heal = (self._base + self._coefficient * self.healer.bonus_healing) * (1 + self.increased_healing) * self._stack
        return floor(heal / self._heal_per_tick)

    def reapply(self):
        self._time_elapsed = self._tick_period
        if self._stack < 3:
            self._stack += 1


@attrs(slots=True, repr=False, eq=False)
class REG(Heal):
    _name = attrib(init=False, default='Regrowth')
    _base = attrib(init=False, default=(1215, 1355))
    _coefficient = attrib(init=False, default=.3 * 1.2)
    _healing_multiplier = attrib(init=False, default=0)
    _crit_multiplier = attrib(init=False, default=.03)
    cast_time = attrib(init=False, default=2)

    def next(self):
        return REGHoT(self.healer)


@attrs(slots=True, repr=False, eq=False)
class REGHoT(HoT):
    _name = attrib(init=False, default='Regrowth')
    _base = attrib(init=False, default=1274)
    _coefficient = attrib(init=False, default=.7 * 1.2)
    _duration = attrib(init=False, default=21)
    _tick_period = attrib(init=False, default=3)
    _healing_multiplier = attrib(init=False, default=.1)
    cast_time = attrib(init=False, default=0)


@attrs(slots=True, repr=False, eq=False)
class HW(Heal):
    _name = attrib(init=False, default='Healing Wave')
    _base = attrib(init=False, default=(2134, 2437))
    _coefficient = attrib(init=False, default=.857 * 1.1)
    _healing_multiplier = attrib(init=False, default=0)
    _crit_multiplier = attrib(init=False, default=.05)
    cast_time = attrib(init=False, default=2.5)

    healing_way = attrib(default=3, type=int)

    def apply(self):
        # TODO correctly apply Healing Way
        coefficient = self._coefficient + self.healing_way * .06

        base_heal = uniform(self._base[0], self._base[1])
        heal = (base_heal + coefficient * self.healer.bonus_healing) * (1 + self.increased_healing)

        roll = random()
        if roll < (self.healer.crit + self.increased_crit):
            return floor(heal * 1.5)
        else:
            return floor(heal)

    @healing_way.validator
    def valid_way(self, attribute, value):
        if not type(value, int):
            raise TypeError("healing_way is not a valid number")
        if not 0 <= value <= 3:
            raise ValueError("healing_way is not a valid number")


@attrs(slots=True, repr=False, eq=False)
class LHW(Heal):
    _name = attrib(init=False, default='Lesser Healing Wave')
    _base = attrib(init=False, default=(1039, 1186))
    _coefficient = attrib(init=False, default=.428 * 1.1)
    _healing_multiplier = attrib(init=False, default=0)
    _crit_multiplier = attrib(init=False, default=.05)
    cast_time = attrib(init=False, default=1)


@attrs(slots=True, repr=False, eq=False)
class CH5(Heal):
    _name = attrib(init=False, default='Chain Heal (Rank 5)')
    _base = attrib(init=False, default=(826, 943))
    _coefficient = attrib(init=False, default=.714 * 1.1)
    _healing_multiplier = attrib(init=False, default=0.2)
    _crit_multiplier = attrib(init=False, default=.05)
    cast_time = attrib(init=False, default=2.5)

    jump = attrib(default=1, type=int)

    def apply(self):
        base_heal = uniform(self._base[0], self._base[1])
        heal = (base_heal + self._coefficient * self.healer.bonus_healing) * (1 + self.increased_healing)
        if self.jump == 0:
            pass
        elif self.jump == 1:
            heal /= 2
        else:
            heal /= 4

        roll = random()
        if roll < (self.healer.crit + self.increased_crit):
            return floor(heal * 1.5)
        else:
            return floor(heal)

    @jump.validator
    def valid_jump(self, attribute, value):
        if not type(value, int):
            raise TypeError("jump is not a valid number")
        if not 0 <= value <= 3:
            raise ValueError("jump is not a valid number")


@attrs(slots=True, repr=False, eq=False)
class CH4(CH5):
    _name = attrib(init=False, default='Chain Heal (Rank 4)')
    _base = attrib(init=False, default=(605, 692))


@attrs(slots=True, repr=False, eq=False)
class ES(Heal):

    def __init__(self, name: str, base: int, cast: float, coefficient: float, healer, charges: int):
        super().__init__(name, (base, base), cast, coefficient, 0, 0, healer)
        self.charges = charges

    def next(self):
        self.charges -= 1
        if self.charges == 0:
            return
        return self
