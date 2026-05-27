from . import basiclib as basiclib
from . import room as room
from . import spell as spell
from . import enemies as enemies
from . import creatures as creatures

from .basiclib import when, say
from .player import Player
from . import utils as utils

import random
from copy import deepcopy

import os

class GameDescription:
    def __init__(self):
        self.player = Player()

        self.starting_room = None

def get_random_enemy():
    global rpg_game

    return deepcopy(random.choice(rpg_game.defined_enemies))

def describe_enemies(room):
    if len(room.enemies) == 0:
        return
    say("Enemies here:")
    for i, enemy in enumerate(room.enemies):
        say("%s: %s (HP %s/%s)" % (
            i,
            enemy.name,
            enemy.current_HP,
            enemy.max_HP
        ))


def room_label(room):
    name = getattr(room, 'name', '?')
    digits = ''.join(c for c in name if c.isdigit())
    if digits:
        return digits[-2:]
    return name[:2]


def describe_room_tags(room):
    return "%s, danger %s, loot %s%%" % (
        getattr(room, 'biome', 'unknown'),
        getattr(room, 'danger', 0),
        getattr(room, 'loot_chance', 0)
    )


def discover_room(room):
    global rpg_game
    if room.discovered:
        return
    room.discovered = True
    rpg_game.player.room_discovery_log.append(room)
    say("Room discovered: %s (%s)" % (
        getattr(room, 'name', 'Unknown room'),
        describe_room_tags(room)
    ))


class Enemy(enemies.Enemy):
    """Reimplement"""


class SpellType(spell.SpellType):
    """Reimplement"""


class Spell(spell.Spell):
    """Reimplement"""


class Creature(creatures.Creature):
    """Reimplement"""


class Room(room.Room):
    """Reimplement"""


class Bag(basiclib.Bag):
    """Reimplement"""


class Item(basiclib.Item):
    """Reimplement"""

@when('where am i')
def whereami():
    global rpg_game
    room = rpg_game.current_room
    say("You are in " + room.name)

@when('directions history')
def show_directions_history():
    global rpg_game
    for d in rpg_game.player.directions_history:
        say(d)    

@when('directions')
def available_directions():
    global rpg_game
    directions = rpg_game.current_room.known_directions
    if len(directions) == 0:
        say("You don't know any direction from this place")
    else:
        str_directions = 'You have already gone to '
        for i in range(0, len(directions)):
            d = directions[i]
            if len(directions) > 1 and i == len(directions) - 1:
                str_directions = str_directions + ' and ' + d
            elif i == len(directions) - 1:
                str_directions = str_directions + d
            elif len(directions) > 0 and i > 0:
                str_directions = str_directions + ', ' + d
            else:
                str_directions = str_directions + d
        say(str_directions)


@when('room log')
def show_room_log():
    global rpg_game
    if len(rpg_game.player.room_discovery_log) == 0:
        say("You have not discovered any rooms yet.")
    else:
        say("Discovered rooms:")
        for i, room in enumerate(rpg_game.player.room_discovery_log):
            say("%s. %s (%s)" % (
                i + 1,
                getattr(room, 'name', 'Unknown room'),
                describe_room_tags(room)
            ))
    rpg_game.should_update_turn = False


@when('map')
@when('mini map')
def show_map():
    global rpg_game
    starting_room = rpg_game.starting_room or rpg_game.current_room
    discover_room(rpg_game.current_room)

    direction_offsets = {
        'north': (0, -1),
        'south': (0, 1),
        'east': (1, 0),
        'west': (-1, 0)
    }
    coords = {starting_room: (0, 0)}
    queue = [starting_room]

    while queue:
        room = queue.pop(0)
        x, y = coords[room]
        for direction, offset in direction_offsets.items():
            next_room = room.exit(direction)
            if next_room is None or not next_room.discovered:
                continue
            if next_room not in coords:
                coords[next_room] = (x + offset[0], y + offset[1])
                queue.append(next_room)

    if rpg_game.current_room not in coords:
        coords[rpg_game.current_room] = (0, 0)

    min_x = min(x for x, _ in coords.values())
    max_x = max(x for x, _ in coords.values())
    min_y = min(y for _, y in coords.values())
    max_y = max(y for _, y in coords.values())

    say("Mini-map:")
    for y in range(min_y, max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            room = None
            for mapped_room, room_coords in coords.items():
                if room_coords == (x, y):
                    room = mapped_room
                    break
            if room is None:
                row.append(" . ")
            elif room is rpg_game.current_room:
                row.append("@%s" % room_label(room))
            else:
                row.append(" %s" % room_label(room))
        say(" ".join(row))

    current_room = rpg_game.current_room
    say("Current: %s (%s)" % (
        getattr(current_room, 'name', 'Unknown room'),
        describe_room_tags(current_room)
    ))
    if current_room.known_directions:
        say("Known directions here: " + ", ".join(current_room.known_directions))
    else:
        say("Known directions here: none")
    rpg_game.should_update_turn = False


@when('north', direction='north')
@when('south', direction='south')
@when('east', direction='east')
@when('west', direction='west')
def go(direction):
    global rpg_game
    room = rpg_game.current_room.exit(direction)
    if room is None:
        say("You can't go " + direction)
    else:
        rpg_game.player.add_direction(direction)
        rpg_game.current_room.add_known_direction(direction)
        room.add_known_direction(room._directions[direction])

        last_room = rpg_game.current_room
        rpg_game.current_room = room
        say('You go %s.' % direction)
        discover_room(room)
        enemy_count = len(room.enemies)
        look()
        if room is not last_room:
            room.on_player_enter()
            if len(room.enemies) != enemy_count:
                describe_enemies(room)


@when('consume ITEM')
def consume(item):
    global rpg_game
    obj = rpg_game.player.inventory.take(item)
    if obj and obj.is_consumable:
        say('You pick up the %s.' % obj)
        obj.consume(rpg_game)
    else:
        say('There is no %s here.' % item)


@when('take ITEM')
def take(item):
    global rpg_game
    obj = rpg_game.current_room.items.take(item)
    if obj:
        say('You pick up the %s.' % obj)
        rpg_game.player.inventory.add(obj)
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
    describe_enemies(rpg_game.current_room)
    if rpg_game.current_room.items:
        for i in rpg_game.current_room.items:
            say('A %s is here.' % i)

@when('inventory')
def show_inventory():
    say('You have:')
    global rpg_game
    for thing in rpg_game.player.inventory:
        say(thing)
    rpg_game.should_update_turn = False
    say("")
    say("Coins: %s" % (rpg_game.player.coins,))

@when('cast list')
def list_magic():
    global rpg_game
    i = 0
    for m in rpg_game.player.learned_spells:
        cooldown = rpg_game.player.get_spell_cooldown(m)
        if cooldown > 0:
            say(str(i) + ': ' + m.name + ' (' + m.get_combat_summary() +
                    ', ready in ' + str(cooldown) + ' turn(s))')
        else:
            say(str(i) + ': ' + m.name + ' (' + m.get_combat_summary() + ')')
        i = i + 1
    rpg_game.should_update_turn = False

@when('cast', magic=None)
@when('cast MAGIC')
def cast(magic):
    global rpg_game
    if magic == None:
        say("Which magic you would like to spell?")
        rpg_game.should_update_turn = False
        return
    i = 0
    wm = magic.strip().split()
    if len(wm) == 0:
        say("Which magic you would like to spell?")
        rpg_game.should_update_turn = False
        return
    for m in rpg_game.player.learned_spells:
        magic_name_size = len(m.name)
        if (utils.is_int(wm[0]) and int(wm[0]) == i):
            m.cast(rpg_game.player, rpg_game, magic[len(wm[0]):])
            break
        elif len(magic) >= magic_name_size and \
            magic[:magic_name_size].lower() == m.name.lower():
            # print(magic)
            m.cast(rpg_game.player, rpg_game, magic[magic_name_size:])
            break
        i = i + 1
    else:
        say("No spell identified.")
        rpg_game.should_update_turn = False

@when('invoke list')
def list_invokable_creatures():
    global rpg_game
    i = 0
    for c in rpg_game.player.learned_invokable_creatures:
        say(str(i) + ': ' + c.name)
        i = i + 1
    rpg_game.should_update_turn = False

@when('invoke', creature = None)
@when('invoke CREATURE')
def invoke(creature):
    global rpg_game
    if creature == None:
        say("Which creature you would like to invoke?")
        return
    i = 0
    wc = creature.strip().split()
    for c in rpg_game.player.learned_invokable_creatures:
        creature_name_size = len(c.name)
        if (utils.is_int(wc[0]) and int(wc[0]) == i) or (\
            len(creature) >= creature_name_size and \
            creature[:creature_name_size].lower() == c.name.lower()):
            # print(magic)
            c.invoke(rpg_game, creature[creature_name_size:])
            break
        i = i + 1

@when('creatures list')
def list_creatures():
    global rpg_game
    i = 0
    for c in rpg_game.player.creatures:
        say(str(i) + ': ' + c.name)
        i = i + 1
    rpg_game.should_update_turn = False

@when('creatures status CREATURE')
def show_creature_status(creature):
    global rpg_game
    if creature == None:
        say("Which creature you would like to invoke?")
        return
    i = 0
    wc = creature.strip().split()
    for c in rpg_game.player.creatures:
        creature_name_size = len(c.name)
        if (utils.is_int(wc[0]) and int(wc[0]) == i) or (\
            len(creature) >= creature_name_size and \
            creature[:creature_name_size].lower() == c.name.lower()):
            # print(magic)
            c.show_status()
            break
        i = i + 1
    rpg_game.should_update_turn = False

@when('alias NAME CMD')
def alias(name, cmd):
    # Method is handled before. So that line is not executed
    say("Creating alias " + name + " equal to " + cmd)

@when('status')
def status():
    global rpg_game
    rpg_game.player.status()
    rpg_game.should_update_turn = False

@when('level reward', reward=None)
@when('level reward REWARD')
def level_reward(reward):
    global rpg_game
    rpg_game.player.claim_level_reward(reward)
    rpg_game.should_update_turn = False

@when('spell unlocks')
@when('spell unlock list')
def spell_unlocks():
    global rpg_game
    rpg_game.player.say_spell_unlock_options()
    rpg_game.should_update_turn = False

@when('stats')
@when('stat points')
def show_stats():
    global rpg_game
    rpg_game.player.say_stats()
    rpg_game.should_update_turn = False

@when('spend stat STAT')
def spend_stat(stat):
    global rpg_game
    rpg_game.player.spend_stat_point(stat)
    rpg_game.should_update_turn = False


def world_update():
    global rpg_game
    for c in rpg_game.player.creatures:
        c.update_action(rpg_game)
    for e in rpg_game.current_room.enemies:
        e.update_action(rpg_game)
    rpg_game.player.update_spell_cooldowns()


def start(description_object):
    global rpg_game
    rpg_game = description_object.get_description()
    discover_room(rpg_game.current_room)
    read_config_file()
    # rpg_game.daiy_log
    look()
    basiclib.start(rpg_game, world_update)

def read_config_file():
    print('Reading config file...')
    file_path = os.environ['GGJ18_DATA_DIR'] + '/config.actions'

    if not os.path.exists(file_path):
        print('There is no config file!\n')
        return


    with open(file_path, 'r') as f:
        config_lines = f.readlines()

    for l in config_lines:
        l = l .strip()
        basiclib._handle_command(l, False)

    print('Config file loaded successfuly!\n')
