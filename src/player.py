from basiclib import say

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

        self.directions_history = []

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

    def add_direction(self, direction):
        self.directions_history.append(direction)