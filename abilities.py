from attr import attrs, attrib
from typing import Tuple


@attrs(slots=True)
class Ability:
    name = attrib(type=str)
    damage = attrib(type=Tuple)
    period = attrib(type=float)
    school = attrib(type=str)

    def apply(self):
        return self.damage


meteor_slash = Ability('Meteor Slash', (20000/9, 20000/9), 15, 'fire')


@attrs(slots=True)
class ArcaneBuffet(Ability):
    inc_damage = attrib(default=500, type=int)
    inc_duration = attrib(default=40, type=int)
    stacks = attrib(default=0, type=int)

    def apply(self):
        damage = self.damage + self.inc_damage * self.stacks
        self.stacks += 1
        return damage


arcane_buffet = ArcaneBuffet('Arcane Buffet', (463, 537), 8, 'arcane')