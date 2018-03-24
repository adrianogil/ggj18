from basiclib import when, say
import basiclib

from dice import Dice

import spell
import enemies
import creatures

import utils

import random
import sys

class Player:
    def __init__(self):
        self.inventory = None
        self.level = 1
        
        self.max_HP = 10
        self.current_HP = self.max_HP

        self.max_MP = 15
        self.current_MP = self.max_MP

        self.creatures = []

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
        say("Wizard Owl Lv " + str(self.level))
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


class Room(basiclib.Room):
    """Reimplement"""

    def set_name(self, name):
        self.name = name

        return self

    def set_player_enter_callback(self, callback):
        self.enter_callback = callback;

    def set_player_stay_callback(self, callback):
        self.stay_callback = callback;

    def set_player_exit_callback(self, callback):
        self.exit_callback = callback;

    def on_player_enter(self):
        if self.enter_callback is not None:
            self.enter_callback(self)

    def on_player_stay(self):
        self.stay_callback(self)

    def on_player_exit(self):
        self.exit_callback(self)

    def set_enemies(self, enemies):
        for e in enemies:
            e.current_room = self
        self.enemies = enemies


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
        last_room = rpg_game.current_room
        rpg_game.current_room = room
        say('You go %s.' % direction)
        look()
        if room != last_room:
            room.on_player_enter()



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
    # rpg_game.daiy_log
    look()
    basiclib.start(rpg_game, world_update)