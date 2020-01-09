from __future__ import annotations
from collections import deque
from heals import Heal
from typing import List
import attr

@attr.s(slots=True)
class Event(object):

    @classmethod
    def next(cls, queue: deque) -> List[Event]:
        pass


@attr.s(slots=True)
class HealerEvent(Heal, Event):

    @classmethod
    def next(cls, queue: deque) -> List[Event]:

        return Heal


@attr.s(slots=True)
class HoTEvent(Hot, Event):

    @classmethod
    def next(cls, queue: deque) -> List[Event]:

        return



class Ability:

    def __init__(self, name, damage, atk_speed, school):
        self.name = name
        self.damage = damage
        self.atk_speed = atk_speed
        self.school = school

        self.atk_timer = atk_speed





meteor_slash = Ability('Meteor Slash', 20000/9, 15, 'fire')
