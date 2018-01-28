from basiclib import say

class Creature:
    def __init__(self, name, MP_cost):
        self.name = name
        self.MP_cost = MP_cost

    def clone(self):
        return Creature(self.name, self.MP_cost)

    def invoke(self, game_description, params):
        params = params.strip()
        wparams = params.strip().split()
        if game_description.player.use_MP(self.MP_cost):
            game_description.player.creatures = self.clone()
            say(self.name + ' was invoked')

creatures_list = {
    "Little demon" : Creature("Little demon", 4)
}