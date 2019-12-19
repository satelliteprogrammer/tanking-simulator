from collections import deque
import encounter
import units

def run(fight : encounter.Fight):

    R = 1000
    r = 0

    while r < R:
        events = deque()
        fight.initialize(events)
        while len(events) > 0:
            do(t)

        r += 1


pumpkinpie = units.Tank('paladin', 500, 140, 100, 300, 250, 600)
brutallus = units.Boss('Brutallus', [11521, 22721], 1, 'physical')
Nilen = units.Healer('paladin', 1400, 0, 200)

fight = encounter.Fight(brutallus, pumpkinpie, Nilen, 480)

run(fight)