from basiclib import say

from grammar import SimpleGrammar

from dice import Dice

class SpellType:
    Attack = 1
    Cure = 2


class Spell:
    def __init__(self, name, description, spell_type):
        self.name         = name
        self.description  = description # A Grammar
        self.spell_type   = spell_type

        self.min_damage = 0
        self.max_damage = 0

        self.target_number = 1


    def set_target_number(self, target_number):
        self.target_number = target_number

        return self

    def set_damage(self, damage_dice):
        self.damage_dice = damage_dice

        return self

    def set_MP_cost(self, MP_cost):
        self.MP_cost = MP_cost

        return self

    def cast(self, caster, game_description, params):
        # print(params)
        say('Casting spell "' + self.name + '"')
        params = params.strip()
        wparams = params.strip().split()
        if game_description.player.use_MP(self.MP_cost):
            if self.spell_type == SpellType.Attack:
                for e in game_description.current_room.enemies:
                    enemy_name_size = len(e.name)
                    if self.target_number == -1 or ( \
                        len(params) >= enemy_name_size and \
                        params[:enemy_name_size].lower() == e.name.lower()):
                        self.description.add_tag("target", [e.name])
                        say(self.description)
                        damage = Dice.parse(self.damage_dice)
                        e.receive_damage(damage, caster)
                        if self.target_number > 1:
                            params = params[enemy_name_size:].strip()
                            self.target_number = self.target_number - 1
                        elif self.target_number != -1:
                            break
                else:
                    if self.target_number != -1:
                        say('No target identified')

    def get_description(self):
        self.description.add_tag("target", "its target")
        say(e.description)
