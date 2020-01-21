from collections import deque, namedtuple
from mechanics import TimeEvent
from os import urandom
from utils import *
import mechanics
import random
import units


class Fight:

    def __init__(self, boss: units.Boss, tank: units.Tank, healer: units.Healer, duration,
                 events: Queue = Queue(), order: Order = Order.RANDOM):
        self.boss = boss
        self.tank = tank
        self.healer = healer
        self.duration = duration
        self.order = order

        self.tank_hp = TankHP(tank.hp)

        self.stats = Statistics()
        self.stats.set_tank_hp(self.tank_hp)

        self.current_time = 0
        self.queue = events

    def initialize(self):
        self.queue.append(TimeEvent(0, self.tank.attack))
        self.queue.append(TimeEvent(0, self.boss.attack))
        self.queue.append(TimeEvent(0, self.healer.heal))

    def finish(self) -> (Statistics, int):
        return self.stats, self.current_time

    def next(self) -> None:
        e = self.queue.popleft()

        self.current_time = e.time

        if self.current_time > self.duration:
            raise FightOver

        # current_events = dict()
        # current_events[str(e[1].__name__)] = e
        if self.queue[0].time == self.current_time:
            self.stats.critical_event()
            # e = self.events.popleft()
            # current_events[str(e[1].__name__)] = e

        e.next(self)

        if self.tank_hp.get_hp() == 0:
            raise FightOver
