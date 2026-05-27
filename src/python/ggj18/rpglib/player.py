from .basiclib import say
import sys


class Player:
    HP_LEVEL_REWARD = 5
    MP_LEVEL_REWARD = 4
    STAT_POINTS_LEVEL_REWARD = 2
    STAT_HP_BONUS = 2
    STAT_MP_BONUS = 2

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
        self.learned_spells = []
        self.defined_spells = {}
        self.spell_cooldowns = {}
        self.pending_level_rewards = 0
        self.stat_points = 0
        self.stats = {
            'vitality': 0,
            'willpower': 0,
            'power': 0
        }

        self.directions_history = []
        self.room_discovery_log = []

    def get_exp_for_next_level(self):
        return self.level * 100

    def set_max_HP(self, max_HP):
        self.max_HP = max_HP
        self.current_HP = self.max_HP

    def set_max_MP(self, max_MP):
        self.max_MP = max_MP
        self.current_MP = self.max_MP

    def add_max_HP(self, max_HP):
        self.max_HP = self.max_HP + max_HP
        self.current_HP = self.current_HP + max_HP

    def add_max_MP(self, max_MP):
        self.max_MP = self.max_MP + max_MP
        self.current_MP = self.current_MP + max_MP

    def is_dead(self):
        return self.current_HP <= 0

    def get_health_str(self):
        return str(self.current_HP) + "/" + str(self.max_HP)

    def get_mana_str(self):
        return str(self.current_MP) + "/" + str(self.max_MP)

    def status(self):
        say("Wizard Owl Lv " + str(self.level) + " (XP " +
            str(self.experience_points) + "/" + str(self.get_exp_for_next_level()) + ')')
        say("HP " + self.get_health_str())
        say("MP " + self.get_mana_str())
        say("Stats: vitality %s, willpower %s, power %s" % (
            self.stats['vitality'],
            self.stats['willpower'],
            self.stats['power']
        ))
        if self.stat_points > 0:
            say("Unspent stat points: %s" % self.stat_points)
        if self.pending_level_rewards > 0:
            say("Pending level rewards: %s. Use 'level reward' to choose." %
                self.pending_level_rewards)

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

    def get_spell_cooldown(self, spell):
        cooldown = self.spell_cooldowns.get(spell.name)
        if cooldown is None:
            return 0
        return cooldown['turns']

    def start_spell_cooldown(self, spell):
        if spell.cooldown > 0:
            self.spell_cooldowns[spell.name] = {
                'turns': spell.cooldown,
                'fresh': True
            }

    def update_spell_cooldowns(self):
        finished_spells = []
        for spell_name, cooldown in self.spell_cooldowns.items():
            if cooldown['fresh']:
                cooldown['fresh'] = False
            else:
                cooldown['turns'] = cooldown['turns'] - 1
            if cooldown['turns'] <= 0:
                finished_spells.append(spell_name)
        for spell_name in finished_spells:
            del self.spell_cooldowns[spell_name]

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
        while self.experience_points >= self.get_exp_for_next_level():
            xp_next_level = self.get_exp_for_next_level()
            self.level = self.level + 1
            self.experience_points = self.experience_points - xp_next_level
            self.pending_level_rewards = self.pending_level_rewards + 1
            say("Wizard Owl reached level %s!" % self.level)
            say("Choose a reward with 'level reward'.")

    def get_available_spell_unlocks(self):
        learned_spell_names = set(spell.name for spell in self.learned_spells)
        spells = []
        for spell_name in self.defined_spells:
            spell = self.defined_spells[spell_name]
            if spell.name not in learned_spell_names:
                spells.append(spell)
        return spells

    def say_level_reward_options(self):
        if self.pending_level_rewards <= 0:
            say("There are no pending level rewards.")
            return
        say("Choose one level reward:")
        say("hp - gain +%s max HP." % self.HP_LEVEL_REWARD)
        say("mp - gain +%s max MP." % self.MP_LEVEL_REWARD)
        if len(self.get_available_spell_unlocks()) > 0:
            say("spell NAME - learn one locked spell.")
        say("stats - gain %s stat points." % self.STAT_POINTS_LEVEL_REWARD)

    def say_spell_unlock_options(self):
        spells = self.get_available_spell_unlocks()
        if len(spells) == 0:
            say("There are no locked spells left to learn.")
            return
        say("Locked spells:")
        for i, spell in enumerate(spells):
            say("%s: %s (%s)" % (i, spell.name, spell.get_combat_summary()))

    def find_spell_unlock(self, spell_choice):
        spells = self.get_available_spell_unlocks()
        spell_choice = spell_choice.strip().lower()
        if spell_choice.isdigit():
            spell_index = int(spell_choice)
            if spell_index >= 0 and spell_index < len(spells):
                return spells[spell_index]
            return None
        exact_matches = []
        prefix_matches = []
        for spell in spells:
            spell_name = spell.name.lower()
            if spell_choice == spell_name:
                exact_matches.append(spell)
            elif spell_name.startswith(spell_choice):
                prefix_matches.append(spell)
        if len(exact_matches) == 1:
            return exact_matches[0]
        if len(prefix_matches) == 1:
            return prefix_matches[0]
        return None

    def learn_spell(self, spell):
        self.learned_spells.append(spell)
        say("Learned spell: %s." % spell.name)

    def claim_level_reward(self, reward_choice):
        if self.pending_level_rewards <= 0:
            say("There are no pending level rewards.")
            return
        if reward_choice is None or reward_choice.strip() == "":
            self.say_level_reward_options()
            return

        reward_parts = reward_choice.strip().split()
        reward_type = reward_parts[0].lower()

        if reward_type == "hp":
            self.add_max_HP(self.HP_LEVEL_REWARD)
            self.pending_level_rewards = self.pending_level_rewards - 1
            say("Max HP increased by %s. HP %s." % (
                self.HP_LEVEL_REWARD,
                self.get_health_str()
            ))
            return
        if reward_type == "mp":
            self.add_max_MP(self.MP_LEVEL_REWARD)
            self.pending_level_rewards = self.pending_level_rewards - 1
            say("Max MP increased by %s. MP %s." % (
                self.MP_LEVEL_REWARD,
                self.get_mana_str()
            ))
            return
        if reward_type == "stats" or reward_type == "stat":
            self.stat_points = self.stat_points + self.STAT_POINTS_LEVEL_REWARD
            self.pending_level_rewards = self.pending_level_rewards - 1
            say("Gained %s stat points." % self.STAT_POINTS_LEVEL_REWARD)
            self.say_stats()
            return
        if reward_type == "spell":
            if len(reward_parts) == 1:
                self.say_spell_unlock_options()
                return
            spell = self.find_spell_unlock(" ".join(reward_parts[1:]))
            if spell is None:
                say("No locked spell matched that choice.")
                self.say_spell_unlock_options()
                return
            self.learn_spell(spell)
            self.pending_level_rewards = self.pending_level_rewards - 1
            return

        say("Unknown level reward.")
        self.say_level_reward_options()

    def say_stats(self):
        say("Stats: vitality %s, willpower %s, power %s" % (
            self.stats['vitality'],
            self.stats['willpower'],
            self.stats['power']
        ))
        say("Unspent stat points: %s" % self.stat_points)
        say("Spend with 'spend stat vitality', 'spend stat willpower', or 'spend stat power'.")

    def normalize_stat_name(self, stat_name):
        stat_name = stat_name.strip().lower()
        stat_aliases = {
            'hp': 'vitality',
            'health': 'vitality',
            'vitality': 'vitality',
            'mp': 'willpower',
            'mana': 'willpower',
            'willpower': 'willpower',
            'spell': 'power',
            'damage': 'power',
            'power': 'power'
        }
        return stat_aliases.get(stat_name)

    def spend_stat_point(self, stat_name):
        if self.stat_points <= 0:
            say("You do not have any stat points.")
            return
        stat_name = self.normalize_stat_name(stat_name)
        if stat_name is None:
            say("Unknown stat.")
            self.say_stats()
            return

        self.stat_points = self.stat_points - 1
        self.stats[stat_name] = self.stats[stat_name] + 1
        if stat_name == 'vitality':
            self.add_max_HP(self.STAT_HP_BONUS)
            say("Vitality increased to %s. Max HP +%s." % (
                self.stats[stat_name],
                self.STAT_HP_BONUS
            ))
        elif stat_name == 'willpower':
            self.add_max_MP(self.STAT_MP_BONUS)
            say("Willpower increased to %s. Max MP +%s." % (
                self.stats[stat_name],
                self.STAT_MP_BONUS
            ))
        elif stat_name == 'power':
            say("Power increased to %s. Attack spells deal +%s damage." % (
                self.stats[stat_name],
                self.stats[stat_name]
            ))

    def get_spell_damage_bonus(self):
        return self.stats['power']

    def add_direction(self, direction):
        self.directions_history.append(direction)
