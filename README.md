# Tanking Simulator

This is a tanking emulator designed for World of Warcraft The Burning Crusade.

### In development !

This project is still in early development.

## Getting Started

The simulation runs for `R` iterations, which could be decided based on _ìnsert statistical measure_ convergence.

### Fight

The fighting is simulated be retrieving the next `EventTime = namedtuple('Event', 'time')` tuple from the
top of a list of events. This list of event is an approximate FIFO queue, implemented with a `deque` from the collections library.
The next event from the queue is retrieved plus all event occurring at the same time.

In all these scenarios there will be critical events where healing will occur at the same as damage taken.
While the time tuning can decrease the number of these singularities, a lenience value can be used to either favor
damage taken or healing received.

Fights will receive a tank, a boss (or multiple mobs, e.g. Hyjal) and multiple healers.

Further mechanisms, such as healing spells and boss abilities need to be added.

### Tank

Tanks receive all attributes and save them in the `Stats` class. It then loops through all talents and buffs to update
the correspondent attributes. These values are then updated with the formulas for defense, miss, dodge, parry, block and
block value.

The Tank class splits into each Tanking Class class, where the class specific bonuses are specified.

##### TODO
Figure out the correct order for all the buffs and talents.

### Healer

Each healer will have a healing strategy based on the fight's condition (e.g. overall raid damage, mana consumption, etc.).
Pre-casting will be added later, let's start with the assumption that all heal reach the end of the cast.

The Healer class also splits along each healing class.

## License
MIT
