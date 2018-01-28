from basiclib import say

from dice import Dice

from grammar import SimpleGrammar

import random

class EnemyState:
    Idle = 0
    PrepareToAttack = 1
    Attack = 2
    Dead = 3

class Enemy:
    def __init__(self, name):
        self.name = name

        self.STR = 0

        self.attack_target = None
        self.attack_target_name = ""

        self.state = EnemyState.Idle

        self.current_room = None

        self.attacks = []

    def add_attack(self, attack_descripton_grammar, damage_dice):
        self.attacks.append({
            "description_grammar" : attack_descripton_grammar,
            "damage_dice" : damage_dice
            })

        return self

    def setHP(self, HP):
        self.max_HP = HP
        self.current_HP = self.max_HP

        return self

    def is_dead(self):
        return self.current_HP <= 0

    def get_STR_MOD(self):
        if self.STR < 6:
            return 1

        return (self.STR - 6) / 3

    def is_attack_successful(self):
        prob = random.uniform(0, 1)

        return prob > 0.3

    def get_attack_damage(self):
        return int(0.5 * Dice.parse('1d4') * self.get_STR_MOD())

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
            if self.attack_target.is_dead():
                self.state == EnemyState.Idle
            else:
                self.attack(game_description)

    def attack(self, game_description):
        if len(self.attacks) > 0:
            attack = random.choice(self.attacks)
            say(attack['description_grammar']
                    .add_tag('name', [self.name])
                    .add_tag('target', [self.attack_target_name])
                    )
            # print('UpdateAction - Attack')
            if self.is_attack_successful():
                damage = Dice.parse(attack['damage_dice'])
                self.attack_target.receive_damage(damage, self)
                if self.attack_target.is_dead():
                    self.state == EnemyState.Idle
            else:
                say(self.attack_target_name + " dodges attack")

    def receive_damage(self, damage, source):
        say(self.name + " received " + str(damage) + " points of damage")
        self.current_HP = self.current_HP - damage
        if self.current_HP <= 0:
            say(self.name + " is dead.")
            self.state = EnemyState.Dead
        elif self.state == EnemyState.Idle or ( \
             self.attack_target != source   \
            ):
            # Enemy should attack whatever attack him
            self.state = EnemyState.Attack
            self.attack_target = source
            self.attack_target_name = source.name


enemies = [
        Enemy("Kobold")
            .setHP(5)
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is attacking #target# with its claws"
                    ]),
                '1d4')
        # Enemy("Kobold Sr", 10, 20),
        # Enemy("Skull", 5, 25)
    ]