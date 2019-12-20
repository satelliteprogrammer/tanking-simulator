from collections import deque, namedtuple
from random import random
from utils import *
import mechanics
import units

TimeEvent = namedtuple('TimeEvent', ['time', 'event'])


class Fight:

    def __init__(self, boss: units.Boss, tank: units.Tank, healer: units.Healer, duration, events: deque = deque(),
                 order: Order = Order.RANDOM):
        self.boss = boss
        self.tank = tank
        self.healer = healer
        self.duration = duration
        self.order = order

        self.critical_events = 0

        self.missed = 0
        self.dodged = 0
        self.parried = 0
        self.blocked = 0
        self.hit = 0
        self.crushed = 0
        self.crited = 0

        self.tank_hp = tank.get_hp()
        self.events = events

    def initialize(self):
        self.events.append(TimeEvent(0, self.tank.attack))
        self.events.append(TimeEvent(0, self.boss.attack))
        self.events.append(TimeEvent(0, self.healer))

    def next(self):
        current_time = self.events[0].time
        current_events = list()
        while self.events[0].time == current_time:
            e = self.events.popleft()
            current_events.append(e)

        if len(current_events) > 1:
            self.critical_events += 1

            while len(current_events):
                current_events.pop()

        else:
            next_event = self.logic(e)

        self.add(next_event)

        #     if self.order == Order.RANDOM:
        #         if random() < .5:
        #             order = Order.LENIENT
        #         else:
        #             order = Order.HARSH
        #     else:
        #         order = self.order
        #
        #     if order == Order.LENIENT:
        #         if self.heal in current_events:
        #             heal, cast = current_events[self.heal][1](self.tank_hp)
        #             self.events.append(TimeEvent(current_time + cast, self.healer.heal))
        #
        #         if self.defend in current_events:
        #             damage = current_events[self.boss.attack][1]()
        #
        #     else:
        #         if self.defend in current_events:
        #             current_events[self.boss.attack][1]()
        #         if self.heal in current_events:
        #             current_events[self.healer.heal][1]()
        #
        # else:
        #     if self.defend in current_events:
        #         current_events[self.boss.attack][1]()
        #     if self.heal in current_events:
        #         current_events[self.healer.heal][1]()
        #
        # if self.attack in current_events:
        #     next_attack = current_events[self.tank.attack][1]()
        #     self.events.append(TimeEvent(current_time + next_attack, self.tank.attack()))

    def logic(self, e: TimeEvent):
        if isinstance(e[1], units.Boss.attack):
            roll = random() * 100
            if roll < self.tank.stats.miss:
                self.missed += 1
                damage = 0
            elif (roll := roll - self.tank.stats.miss) < self.tank.stats.dodge:
                self.dodged += 1
                damage = 0
            elif (roll := roll - self.tank.stats.dodge) < self.tank.stats.parry:
                self.parried += 1
                damage = 0
            elif (roll := roll - self.tank.stats.parry) < self.tank.stats.block:
                self.blocked += 1
                damage = (1 - self.tank.get_armor_reduction(self.boss.level)) * (e[1]() - self.tank.get_block_reduction())
            elif (roll := roll - self.tank.stats.block) < 15:
                self.crushed += 1
                damage = (1 - self.tank.get_armor_reduction(self.boss.level)) * e[1]() * 1.5
            else:
                self.hit += 1
                damage = (1 - self.tank.get_armor_reduction(self.boss.level)) * e[1]()

            self.tank_hp.damage(damage)
            return TimeEvent(e[0] + self.boss.speed, self.boss.attack)

        elif isinstance(e[1], units.Tank.attack):

            return TimeEvent(e[0] + self.tank.speed, self.tank.attack)

        elif isinstance(e[1], units.Healer.heal):

            heal = e[1]()
            self.tank_hp.heal(heal)

            cast = self.healer.decision(self.tank_hp)
            return TimeEvent(e[0] + cast, self.healer.heal)

        else:
            print('error')

    def add(self, e: TimeEvent):
        for
