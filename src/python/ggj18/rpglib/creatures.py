from .basiclib import say
from .dice import Dice
from . import utils as utils


class CreatureState:
    NonExistant = 0
    Idle = 1
    Attack = 2
    Dead = 3


class Creature:
    def __init__(self, name, MP_cost):
        self.name = name
        self.MP_cost = MP_cost

        self.state = CreatureState.NonExistant

        self.current_room = None

        self.attack_target = None
        self.attack_target_name = ""

        self.directions = ["north", "south", "east", "west"]

        self.current_room = None

        self.cast_time = 0

    def setHP(self, HP):
        self.max_HP = HP
        self.current_HP = self.max_HP

        return self

    def set_damage_dice(self, damage_dice):
        self.damage_dice = damage_dice

        return self

    def set_cast_time(self, cast_time):
        self.cast_time = cast_time

        return self

    def clone(self):
        return Creature(self.name, self.MP_cost) \
                .setHP(self.max_HP) \
                .set_cast_time(self.cast_time) \
                .set_damage_dice(self.damage_dice)

    def is_dead(self):
        return self.current_HP <= 0

    def show_status(self):
        say(self.name + ' HP ' + str(self.current_HP) + '/' + str(self.max_HP))
        say('Time to invoke to finish: ' + str(self.cast_time) + ' turns')

    def invoke(self, game_description, params):
        params = params.strip()
        wparams = params.strip().split()
        if game_description.player.use_MP(self.MP_cost):
            new_creature = self.clone()
            new_creature.state = CreatureState.Idle
            new_creature.current_room = game_description.current_room
            game_description.player.creatures.append(new_creature)
            say(self.name + ' was invoked')

    def go(self, direction):
        room = self.current_room.exit(direction)
        if room:
            last_room = self.current_room
            self.current_room = room
            say(self.name + ' went %s.' % direction)

            return True
            # look()
            # if room != last_room:
            #     room.on_player_enter()
        return False

    def is_attack_successful(self):
        return Dice.parse('1d20') > 8

    def get_attack_damage(self):
        return Dice.parse(self.damage_dice)

    def update_action(self, game_description):
        if self.state == CreatureState.Idle:
            # Verify enemies in current room
            for e in self.current_room.enemies:
                if not e.is_dead():
                    self.attack_target = e
                    self.attack_target_name = e.name
                    say(self.name + ' is going to attack ' + self.attack_target_name)
                    self.state = CreatureState.Attack
                    break
            else:
                # No enemies. Should move? Random move!
                dir = Dice.parse( '1d4')
                if not self.go(self.directions[dir-1]):
                    say(utils.capitalize(self.name) + ' is wandering loosely')
        elif self.state == CreatureState.Attack:
            if self.attack_target.is_dead():
                self.state = CreatureState.Idle
            else:
                say(self.name + " is attacking " + self.attack_target_name)
                # print('UpdateAction - Attack')
                if self.is_attack_successful():
                    damage = self.get_attack_damage()
                    self.attack_target.receive_damage(damage, self)
                    if self.attack_target.is_dead():
                        self.state = CreatureState.Idle
                else:
                    say(self.attack_target_name + " dodges attack")

        self.cast_time = self.cast_time - 1
        if self.cast_time <= 0:
            say(self.name + "'s invocation finished.")
            game_description.player.creatures.remove(self)

    def receive_damage(self, damage, source):
        say(self.name + " received " + str(damage) + " points of damage")
        self.current_HP = self.current_HP - damage
        if self.current_HP <= 0:
            say(self.name + " is dead.")
            self.state = CreatureState.Dead
        elif self.state == CreatureState.Idle or ( \
             self.attack_target != source   \
            ):
            # Creature should attack whatever attack him
            self.state = CreatureState.Attack
            self.attack_target = source
            self.attack_target_name = source.name