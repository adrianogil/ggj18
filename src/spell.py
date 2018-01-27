from basiclib import say

class SpellType:
    Attack = 1
    Cure = 2

class Spell:
    def __init__(self, name, description, spell_type):
        self.name         = name
        self.description  = description
        self.spell_type   = spell_type

        self.min_damage = 0
        self.max_damage = 0

    def set_damage(self, min_damage, max_damage):
        self.min_damage = min_damage
        self.max_damage = max_damage

        return self

    def cast(self, game_description, params):
        say(self.description)
        wparams = params.split()
        print(params)
        if self.spell_type == SpellType.Attack:
            for e in game_description.current_room.enemies:
                enemy_name_size = len(e.name)
                if len(params) >= enemy_name_size and \
                   params[:enemy_name_size].lower() == e.name.lower():
                   print(e.name)



spell_list = {
    "Magic missiles" : Spell("Magic missiles", 
                         "A missile of magical energy darts forth from your fingertip and strikes its target",
                         SpellType.Attack)
                    .set_damage(3,7)
}