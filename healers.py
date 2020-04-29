from attr import attrs, attrib
from heals import *
from units import Healer
from utils import TankHP


@attrs(slots=True, repr=False, eq=False)
class PaladinHealer(Healer):

    def decision(self, time: float, tank: TankHP):
        if tank.get_hp() < .8 * tank.full:
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
