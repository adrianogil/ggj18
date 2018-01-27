from adventurelib import when
import adventurelib

class Player:
    def __init__(self):
        self.inventory = None

class GameDescription:
    def __init__(self):
        self.player = Player()

        self.starting_room = None

class Enemy:
    def __init__(self):
        self.health_points = 10


class Room(adventurelib.Room):
    """Reimplement"""


class Bag(adventurelib.Bag):
    """Reimplement"""


class Item(adventurelib.Item):
    """Reimplement"""


@when('north', direction='north')
@when('south', direction='south')
@when('east', direction='east')
@when('west', direction='west')
def go(direction):
    global current_room
    room = current_room.exit(direction)
    if room:
        current_room = room
        say('You go %s.' % direction)
        look()
        if room == magic_forest:
            set_context('magic_aura')
        else:
            set_context('default')


@when('take ITEM')
def take(item):
    obj = current_room.items.take(item)
    if obj:
        say('You pick up the %s.' % obj)
        inventory.add(obj)
    else:
        say('There is no %s here.' % item)


@when('drop THING')
def drop(thing):
    obj = inventory.take(thing)
    if not obj:
        say('You do not have a %s.' % thing)
    else:
        say('You drop the %s.' % obj)
        current_room.items.add(obj)


@when('look')
def look():
    say(current_room)
    if current_room.items:
        for i in current_room.items:
            say('A %s is here.' % i)


@when('inventory')
def show_inventory():
    say('You have:')
    for thing in inventory:
        say(thing)

@when('cast', context='magic_aura', magic=None)
def cast(magic):
    if magic == None:
        say("Which magic you would like to spell?")

def start(description_object):
    game_description = description_object.get_description()
    adventurelib.start()