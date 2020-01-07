from collections import deque, namedtuple
from os import urandom
from utils import *
import mechanics
import random
import units


class Fight:

    def __init__(self, boss: units.Boss, tank: units.Tank, healer: units.Healer, duration,
                 events: deque = deque(), order: Order = Order.RANDOM):
        self.boss = boss
        self.tank = tank
        self.healer = healer
        self.duration = duration
        self.order = order

        self.tank_hp = TankHP(tank.hp)

        self.stats = Statistics()
        self.stats.set_tank_hp(self.tank_hp)

        self.current_time = 0
        self.events = events

    def initialize(self):
        self.events.append(TimeEvent(0, self.tank.attack))
        self.events.append(TimeEvent(0, self.boss.attack))
        self.events.append(TimeEvent(0, self.healer.heal))

    def finish(self) -> (Statistics, int):
        return self.stats, self.current_time

    def next(self) -> None:
        e = self.events.popleft()

        self.current_time = e.time

        if self.current_time > self.duration:
            raise FightOver

        # current_events = dict()
        # current_events[str(e[1].__name__)] = e
        if self.events[0].time == self.current_time:
            self.stats.critical_event()
            # e = self.events.popleft()
            # current_events[str(e[1].__name__)] = e

        next_event = e.event.next()

        if self.tank_hp.get_hp() == 0:
            raise FightOver

        self.add(next_event)

    def logic(self, e: TimeEvent):

        if e.event == self.boss.attack:
            roll = random.uniform(0, 100)
            if roll < self.tank.stats.miss:
                self.stats.miss()
            elif (roll := roll - self.tank.stats.miss) < self.tank.stats.dodge:
                self.stats.dodge()
            elif (roll := roll - self.tank.stats.dodge) < self.tank.stats.parry:
                self.stats.parry()
            elif (roll := roll - self.tank.stats.parry) < self.tank.stats.block:
                self.stats.block()
                damage = ((1 - self.tank.get_armor_reduction(self.boss.level)) *
                          (e.event() - self.tank.get_block_reduction()))
                self.tank_hp.damage(damage, self.current_time)
            elif (roll - self.tank.stats.block) < 15:
                self.stats.crush()
                damage = (1 - self.tank.get_armor_reduction(self.boss.level)) * e.event() * 1.5
                self.tank_hp.damage(damage, self.current_time)
            else:
                self.stats.hit()
                damage = (1 - self.tank.get_armor_reduction(self.boss.level)) * e.event()
                self.tank_hp.damage(damage, self.current_time)

            return TimeEvent(e.time + self.boss.speed, self.boss.attack)

        elif e.event == self.tank.attack:
            return TimeEvent(e.time + self.tank.speed, self.tank.attack)

        elif e.event == self.healer.heal:
            heal = e.event()
            self.tank_hp.heal(heal, self.current_time)

            cast = self.healer.decision(self.tank_hp)
            return TimeEvent(e.time + cast, self.healer.heal)

        else:
            print('error')

    def add(self, e: TimeEvent):
        for i, te in reversed(list(enumerate(self.events))):
            if e.time > te.time:
                self.events.insert(i + 1, e)
                return

        self.events.appendleft(e)
