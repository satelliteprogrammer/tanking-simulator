from heals import Heal
import attr


@attr.s(slots=True)
class Event:

    def next(self):
        pass


@attr.s(slots=True)
class HealEvent(Event, Heal):



class Ability:

    def __init__(self, name, damage, atk_speed, school):
        self.name = name
        self.damage = damage
        self.atk_speed = atk_speed
        self.school = school

        self.atk_timer = atk_speed





meteor_slash = Ability('Meteor Slash', 20000/9, 15, 'fire')
