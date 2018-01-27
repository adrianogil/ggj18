from basiclib import when, say
import basiclib

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


class Room(basiclib.Room):
    """Reimplement"""


class Bag(basiclib.Bag):
    """Reimplement"""


class Item(basiclib.Item):
    """Reimplement"""


@when('north', direction='north')
@when('south', direction='south')
@when('east', direction='east')
@when('west', direction='west')
def go(direction):
    global rpg_game
    room = rpg_game.current_room.exit(direction)
    if room:
        rpg_game.current_room = room
        say('You go %s.' % direction)
        look()


@when('take ITEM')
def take(item):
    global rpg_game
    obj = rpg_game.current_room.items.take(item)
    if obj:
        say('You pick up the %s.' % obj)
        inventory.add(obj)
    else:
        say('There is no %s here.' % item)


@when('drop THING')
def drop(thing):
    global rpg_game
    obj = rpg_game.player.inventory.take(thing)
    if not obj:
        say('You do not have a %s.' % thing)
    else:
        say('You drop the %s.' % obj)
        rpg_game.current_room.items.add(obj)


@when('look')
def look():
    global rpg_game
    say(rpg_game.current_room)
    if rpg_game.current_room.items:
        for i in rpg_game.current_room.items:
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

@when('alias NAME CMD')
def alias(name, cmd):
    say("Creating alias " + name + " equal to " + cmd)

def start(description_object):
    global rpg_game
    rpg_game = description_object.get_description()
    look()
    basiclib.start(rpg_game)