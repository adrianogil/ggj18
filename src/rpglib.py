from basiclib import when, say
import basiclib

import spell

import random

class Player:
    def __init__(self):
        self.inventory = None
        self.level = 1
        
        self.max_HP = 10
        self.current_HP = self.max_HP

        self.max_mana = 15
        self.current_mana = self.max_mana

        self.learned_spells = [
            spell.spell_list["Magic missiles"]
        ]

    def get_health_str(self):
        return str(self.current_HP) + "/" + str(self.max_HP)

    def get_mana_str(self):
        return str(self.current_mana) + "/" + str(self.max_mana)

    def status(self):
        say("Wizard Owl Lv " + str(self.level))
        say("HP " + self.get_health_str())
        say("MP " + self.get_mana_str())

    def receive_damage(self, damage):
        say("Wizard Owl received " + str(damage) + " points of damage")
        self.current_HP = self.current_HP - damage
        if self.current_HP <= 0:
            say("Wizard Owl is dead. ")
            say("Game Over")

class GameDescription:
    def __init__(self):
        self.player = Player()

        self.starting_room = None

class EnemyState:
    Idle = 0
    PrepareToAttack = 1
    Attack = 2
    Dead = 3

class Enemy:
    def __init__(self, name, HP, STR):
        self.name = name

        self.max_HP = HP
        self.current_HP = self.max_HP

        self.STR = STR

        self.attack_target = None
        self.attack_target_name = ""

        self.state = EnemyState.Idle

        self.current_room = None

    def get_STR_MOD(self):
        if self.STR < 6:
            return 1

        return (self.STR) / 2

    def is_attack_successful(self):
        prob = random.uniform(0, 1)

        return prob > 0.3

    def get_attack_damage(self):
        return int(random.uniform(0.6, 1.2) * self.get_STR_MOD())

    def update_action(self, game_description):
        if self.state == EnemyState.Idle:
            if self.current_room == game_description.current_room:
                prob = random.uniform(0, 1)
                if prob < 0.8:
                    say("Player was seen by " + self.name)
                    # In same room than player
                    self.attack_target = game_description.player
                    self.attack_target_name = "player"
                    self.state = EnemyState.Attack
                    say(self.name + " is going to attack " + self.attack_target_name)
                else:
                    say(self.name + " is wandering loosely")
        elif self.state == EnemyState.Attack:
            say(self.name + " is attacking " + self.attack_target_name)
            # print('UpdateAction - Attack')
            if self.is_attack_successful():
                damage = self.get_attack_damage()
                self.attack_target.receive_damage(damage)
            else:
                say(self.attack_target_name + " dodges attack")



def get_random_enemy():
    enemies = [
        Enemy("Kobold", 3, 8),
        Enemy("Kobold Sr", 10, 20),
        Enemy("Skull", 5, 25)
    ]

    return random.choice(enemies)

class Room(basiclib.Room):
    """Reimplement"""

    def set_player_enter_callback(self, callback):
        self.enter_callback = callback;

    def set_player_stay_callback(self, callback):
        self.stay_callback = callback;

    def set_player_exit_callback(self, callback):
        self.exit_callback = callback;

    def on_player_enter(self):
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
    global rpg_game
    for thing in rpg_game.player.inventory:
        say(thing)

@when('cast list')
def list_magic():
    global rpg_game
    for m in rpg_game.player.learned_spells:
        say(m.name)

@when('cast', magic=None)
@when('cast MAGIC')
def cast(magic):
    global rpg_game
    if magic == None:
        say("Which magic you would like to spell?")
    for m in rpg_game.player.learned_spells:
        magic_name_size = len(m.name)
        if magic[:magic_name_size].lower() == m.name.lower():
            m.cast(rpg_game, magic[magic_name_size:])
            break


@when('alias NAME CMD')
def alias(name, cmd):
    # Method is handled before. So that line is not executed
    say("Creating alias " + name + " equal to " + cmd)

@when('status')
def status():
    global rpg_game
    rpg_game.player.status()


def world_update():
    global rpg_game
    for e in rpg_game.current_room.enemies:
        e.update_action(rpg_game)


def start(description_object):
    global rpg_game
    rpg_game = description_object.get_description()
    look()
    basiclib.start(rpg_game, world_update)