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

    def set_damage(self, damage_dice):
        self.damage_dice = damage_dice

        return self

    def set_MP_cost(self, MP_cost):
        self.MP_cost = MP_cost

        return self

    def cast(self, caster, game_description, params):
        # print(params)
        params = params.strip()
        wparams = params.strip().split()
        if game_description.player.use_MP(self.MP_cost):
            if self.spell_type == SpellType.Attack:
                for e in game_description.current_room.enemies:
                    enemy_name_size = len(e.name)
                    if len(params) >= enemy_name_size and \
                       params[:enemy_name_size].lower() == e.name.lower():
                       self.description.add_tag("target", [e.name])
                       say(self.description)
                       damage = Dice.parse(self.damage_dice)
                       e.receive_damage(damage, caster)
                       break
                else:
                    say('No target identified')

    def get_description(self):
        self.description.add_tag("target", "its target")
        say(e.description)



spell_list = {
    "Magic missiles" : Spell("Magic missiles", 
                        SimpleGrammar().set_text("A missile of magical energy darts forth from your fingertip and strikes #target#"),
                         SpellType.Attack)
                    .set_damage('1d4')
                    .set_MP_cost(2)
}