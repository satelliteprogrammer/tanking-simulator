from collections import namedtuple
from random import random
from utils import *
import units

EventTime = namedtuple('Event', 'time')


class Fight:

    def __init__(self, boss: units.Boss, tank: units.Tank, healer: units.Healer, duration):
        self.boss = boss
        self.duration = duration
        self.boss_atk_timer = 0
        self.tank_atk_timer = 0
        self.heal_inc_timer = 0


def do(order: Order):
    if order == Order.LENIENT:
        heal
        boss_hit
    elif order == Order.HARSH:
        boss_hit
        heal
    else:
        if random() < .5:
            boss_hit
            heal
        else:
            heal
            boss_hit

    atk
    ...
