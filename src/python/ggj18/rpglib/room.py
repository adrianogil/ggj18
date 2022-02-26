from .basiclib import InvalidCommand
from .basiclib import InvalidDirection
from .basiclib import Bag

from copy import deepcopy


class Room:
    """A generic room object that can be used by game code."""

    _directions = {}

    @staticmethod
    def add_direction(forward, reverse):
        """Add a direction."""
        for dir in (forward, reverse):
            if not dir.islower():
                raise InvalidCommand(
                    'Invalid direction %r: directions must be all lowercase.'
                )
            if dir in Room._directions:
                raise KeyError('%r is already a direction!' % dir)
        Room._directions[forward] = reverse
        Room._directions[reverse] = forward

        # Set class attributes to None to act as defaults
        setattr(Room, forward, None)
        setattr(Room, reverse, None)

    def __init__(self, description):
        self.description = str(description).strip()
        self.enemies = []
        self.known_directions = []

        self.enter_callback = None
        self.exit_callback = None
        self.stay_callback = None

        # Copy class Bags to instance variables
        for k, v in vars(type(self)).items():
            if isinstance(v, Bag):
                setattr(self, k, deepcopy(v))

    def __str__(self):
        return self.description

    def exit(self, direction):
        """Get the exit of a room in a given direction.

        Return None if the room has no exit in a direction.

        """
        if direction not in self._directions:
            raise KeyError('%r is not a direction' % direction)
        return getattr(self, direction, None)

    def exits(self):
        """Get a list of directions to exit the room."""
        return sorted(d for d in self._directions if getattr(self, d))

    def __setattr__(self, name, value):
        if isinstance(value, Room):
            if name not in self._directions:
                raise InvalidDirection(
                    '%r is not a direction you have declared.\n\n' +
                    'Try calling Room.add_direction(%r, <opposite>) ' % name +
                    ' where <opposite> is the return direction.'
                )
            reverse = self._directions[name]
            object.__setattr__(self, name, value)
            object.__setattr__(value, reverse, self)
        else:
            object.__setattr__(self, name, value)

    def add_known_direction(self, direction):
        if not direction in self.known_directions:
            self.known_directions.append(direction)

    def set_name(self, name):
        self.name = name

        return self

    def set_player_enter_callback(self, callback):
        self.enter_callback = callback;
        return self

    def set_player_stay_callback(self, callback):
        self.stay_callback = callback;
        return self

    def set_player_exit_callback(self, callback):
        self.exit_callback = callback;
        return self

    def on_player_enter(self):
        if self.enter_callback is not None:
            self.enter_callback(self)

    def on_player_stay(self):
        self.stay_callback(self)

    def on_player_exit(self):
        self.exit_callback(self)

    def add_enemy(self, enemy):
        if self.enemies == None:
            self.enemies = [enemy]
        else:
            self.enemies.append(enemy)

    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def set_enemies(self, enemies):
        for e in enemies:
            e.current_room = self
        self.enemies = enemies
        return self


Room.add_direction('north', 'south')
Room.add_direction('east', 'west')