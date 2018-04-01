from basiclib import when, say
import basiclib

import room

from dice import Dice

import spell
import enemies
import creatures

import utils

import random
import sys

import os

class Player:
    def __init__(self):
        self.inventory = None

        self.level = 1
        self.experience_points = 0

        self.coins = 0

        self.max_HP = 10
        self.current_HP = self.max_HP

        self.max_MP = 15
        self.current_MP = self.max_MP

        self.creatures = []

    def get_exp_for_next_level(self):
        return self.level * 100;

    def set_max_HP(self, max_HP):
        self.max_HP = max_HP
        self.current_HP = self.max_HP

    def set_max_MP(self, max_MP):
        self.max_MP = max_MP
        self.current_MP = self.max_MP

    def is_dead(self):
        return self.current_HP <= 0

    def get_health_str(self):
        return str(self.current_HP) + "/" + str(self.max_HP)

    def get_mana_str(self):
        return str(self.current_MP) + "/" + str(self.max_MP)

    def status(self):
        say("Wizard Owl Lv " + str(self.level) + " (XP " + \
            str(self.experience_points) + "/" + str(self.get_exp_for_next_level()) + ')')
        say("HP " + self.get_health_str())
        say("MP " + self.get_mana_str())

    def receive_damage(self, damage, source):
        say("Wizard Owl received " + str(damage) + " points of damage")
        self.current_HP = self.current_HP - damage
        if self.is_dead():
            say("Wizard Owl was slaughtered by " + source.name)
            say("Game Over")
            sys.exit()

    def use_MP(self, MP_usage):
        if self.current_MP >= MP_usage:
            self.current_MP = self.current_MP - MP_usage
            return True
        return False

    def get_victory_from(self, enemy, loot=None):
        self.add_XP(enemy.granted_xp)
        say("Player received %s points of experience." % ( enemy.granted_xp,) )
        if not loot is None:
            if 'coins' in loot:
                say('Player received %s coins' % (loot['coins'],))
                self.coins = self.coins + loot['coins']
            if 'items' in loot:
                for t in loot['items']:
                    say('Player received %s' % (t.name,))
                    self.inventory.add(t)

    def add_XP(self, new_xp):
        self.experience_points = self.experience_points + new_xp
        xp_next_level = self.get_exp_for_next_level()
        if self.experience_points >= xp_next_level:
            self.level = self.level + 1
            self.experience_points = self.experience_points - xp_next_level


class GameDescription:
    def __init__(self):
        self.player = Player()

        self.starting_room = None

def get_random_enemy():
    global rpg_game

    return random.choice(rpg_game.defined_enemies)


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

@when('directions')
def available_directions():
    global rpg_game
    directions = rpg_game.current_room.known_directions
    if len(directions) == 0:
        say("You don't know any direction at this place")
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
        rpg_game.current_room.add_known_direction(direction)
        # if direction == 'north':
        #     room.add_known_direction('south')

        last_room = rpg_game.current_room
        rpg_game.current_room = room
        say('You go %s.' % direction)
        look()
        if room is not last_room:
            room.on_player_enter()


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
        say(str(i) + ': ' + m.name)
        i = i + 1
    rpg_game.should_update_turn = False

@when('cast', magic=None)
@when('cast MAGIC')
def cast(magic):
    global rpg_game
    if magic == None:
        say("Which magic you would like to spell?")
        return
    i = 0
    wm = magic.strip().split()
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


def world_update():
    global rpg_game
    for c in rpg_game.player.creatures:
        c.update_action(rpg_game)
    for e in rpg_game.current_room.enemies:
        e.update_action(rpg_game)


def start(description_object):
    global rpg_game
    rpg_game = description_object.get_description()
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
