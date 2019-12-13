# Tanking Simulator

This is a tanking emulator designed for World of Warcraft The Burning Crusade.

### In development !

This project is still in early development.

## Getting Started

The simulation runs for `R` iterations, which could be decided based on _ìnsert statistical measure_ convergence.

There are three ways of achieving a timeline:

1. The fighting is simulated be retrieving the next `EventTime = namedtuple('Event', 'time')` tuple from the
top of a list of events

2. Discretizing time using an acceptable grid where ΔT < 10x minimum time between events. [ref]

3. Interrupt driven architecture.

In all these scenarios there will be critical events where healing will occur at the same as damage taken.
While the time tuning can decrease the number of these singularities, a lenience value can be used to either favor
damage taken or healing received.

Fights will receive a tank, a boss (or multiple mobs, e.g. Hyjal) and multiple healers.

Further mechanisms, such as healing spells and boss abilities need to be added.

Each healer will have a healing strategy based on the fight's condition (e.g. overall raid damage, mana consumption, etc.).
Pre-casting will be added later, let's start with the assumption that all heal reach the end of the cast.

## License
MIT
