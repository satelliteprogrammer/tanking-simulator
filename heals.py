from math import floor
from random import random, uniform
from statistics import mean
from typing import Tuple
# from units import Healer


class Heal:

    def __init__(self, name: str, base: tuple, cast: float, coefficient: float, inc_healing: float, inc_crit: float, healer):
        self.name = name

        self.base = base
        self.cast_time = max(1.5 / (1 + healer.haste), cast / (1 + healer.haste))
        self.coefficient = coefficient
        self.increased_healing = inc_healing
        self.crit = inc_crit + healer.crit

        self.healer = healer

    def apply(self):
        heal = (uniform(self.base[0], self.base[1]) + self.coefficient * self.healer.bh) * self.increased_healing
        roll = random()
        if roll < self.crit:
            return floor(heal * 1.5)
        else:
            return floor(heal)

    def next(self):
        return None

    def hps(self):
        heal = (mean(self.base) + self.coefficient * self.healer.bh) * (1 + self.increased_healing)

        return (heal * 1.5 * self.crit/100 + heal * (1 - self.crit/100))/self.cast_time

    def get_period(self):
        pass

    def __repr__(self):
        return f'{self.name}'


class HoT(Heal):

    def __init__(self, name: str, base: int, cast: float, coefficient: float, inc_healing: float, healer,
                 stack: int, duration: int, tick_period: int):
        super().__init__(name, (base, base), cast, coefficient, inc_healing, 0, healer)

        self.max_stack = stack
        self.duration = duration
        self.tick_period = tick_period
        self.heal_per_tick = duration/tick_period

        self.elapsed = self.tick_period

    def apply(self):
        if self.elapsed == 0:
            return 0
        else:
            return floor(
                ((self.base[0] + self.coefficient * self.healer.bh) * self.increased_healing)/self.heal_per_tick)

    def next(self):
        self.elapsed += self.tick_period
        if self.elapsed > self.duration:
            return None
        else:
            return self

    def get_period(self):
        return self.tick_period

    def reset(self):
        self.elapsed = self.tick_period


class LB(HoT):

    def __init__(self, name: str, base: int, cast: float, coefficient: float, inc_healing: float, healer, stack: int,
                 duration: int, tick_period: int):
        super().__init__(name, base, cast, coefficient, inc_healing, healer, stack, duration, tick_period)
        self.stack = 1

    def reapply(self):
        self.elapsed = self.tick_period  # TODO verify this
        if self.stack < 3:
            self.stack += 1

    def apply(self):
        return self.stack * super().apply()


class REG(Heal):

    def __init__(self, name: str, base: tuple, cast: float, coefficient: float, inc_healing: float, inc_crit: float,
                 healer):
        super().__init__(name, base, cast, coefficient, inc_healing, inc_crit, healer)

    def next(self):
        self.healer.REG_HOT.reset()
        return self.healer.REG_HOT


class Shield(Heal):

    def __init__(self, name: str, base: int, cast: float, coefficient: float, healer, charges: int):
        super().__init__(name, (base, base), cast, coefficient, 0, 0, healer)
        self.charges = charges

    def next(self):
        self.charges -= 1
        if self.charges == 0:
            return
        return self
