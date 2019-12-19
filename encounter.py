from collections import deque, namedtuple
from random import random
from utils import *
import mechanics
import units

TimeEvent = namedtuple('TimeEvent', ['time', 'event'])


class Fight:

    def __init__(self, boss: units.Boss, tank: units.Tank, healer: units.Healer, duration, order: Order = Order.RANDOM):
        self.boss = boss
        self.tank = tank
        self.healer = healer
        self.duration = duration
        self.boss_atk_timer = 0
        self.tank_atk_timer = 0
        self.heal_inc_timer = 0

        self.order = order
        self.critical_events = 0

    def initialize(self, events: deque):
        events.append(TimeEvent(0, self.tank.attack()))
        events.append(TimeEvent(0, self.boss.attack()))
        events.append(TimeEvent(0, self.healer.heal(10000, 10000)))

    def next(self, events: deque):
        current_time = events[0].time
        current_events = dict()
        while events[0].time == current_time:
            e = events.popleft()
            current_events[e[1]] = (e[0], e[1])

        if len(current_events) > 1:
            self.critical_events += 1
            if self.order == Order.RANDOM:
                if random() < .5:
                    order = Order.LENIENT
                else:
                    order = Order.HARSH
            else:
                order = self.order

            if order == Order.LENIENT:
                if self.healer.heal in current_events:
                    current_events[self.healer.heal][1]()
                if self.boss.attack in current_events:
                    current_events[self.boss.attack][1]()
            else:
                if self.boss.attack in current_events:
                    current_events[self.boss.attack][1]()
                if self.healer.heal in current_events:
                    current_events[self.healer.heal][1]()

        else:
            if self.boss.attack in current_events:
                current_events[self.boss.attack][1]()
            if self.healer.heal in current_events:
                current_events[self.healer.heal][1]()

        if self.tank.attack in current_events:
            current_events[self.tank.attack][1]()
