from attr import attrs, attrib
from heals import *
from units import Healer
from utils import TankHP


@attrs(slots=True, repr=False, eq=False)
class PaladinHealer(Healer):
    last_df = attrib(default=0, type=float)

    divine_favor = 120

    def decision(self, time: float, tank: TankHP):
        if tank.get_hp() < .4 * tank.full and (self.last_df == 0 or time > self.last_df + self.divine_favor):
            self.last_df = time
            return HL11(healer=self, increased_crit=1)
        elif tank.get_hp() < .8 * tank.full:
            return HL9(healer=self)
        else:
            return FoL(healer=self)


@attrs(slots=True, repr=False, eq=False)
class Eydel(PaladinHealer):

    def decision(self, time: float, tank: TankHP):
        if tank.get_hp() < .7 * tank.full:
            return HL11(healer=self)
        else:
            return FoL(healer=self)


@attrs(slots=True, repr=False, eq=False)
class DruidHealer(Healer):
    init = attrib(init=False, default=True)
    counter = attrib(init=False, default=0)

    initial_rotation = ('REJ', 'LB', 'LB', 'LB', 'REG', None, None)
    rotation = ('LB', 'REJ', 'REG', None, 'LB', None, None, None)

    swiftness = 180
    swiftmend = 15

    def decision(self, time: float, tank: TankHP):
        if self.init:
            if cast := self.initial_rotation[self.counter]:
                cast = eval(cast)(healer=self)
            self.counter += 1
            if self.counter > 6:
                self.init = False
                self.counter = 0
        else:
            if cast := self.rotation[self.counter]:
                cast = eval(cast)(healer=self)
            self.counter += 1
            if self.counter > 7:
                self.counter = 0

        return cast


@attrs(slots=True, repr=False, eq=False)
class ShamanHealer(Healer):

    def decision(self, time: float, tank: TankHP):
        return CH4(healer=self)
