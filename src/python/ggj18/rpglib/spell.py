from .basiclib import say
from .dice import Dice


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
        self.damage_dice = '0'
        self.MP_cost = 0
        self.hit_chance = 1.0
        self.cooldown = 1

        self.target_number = 1

    def set_cooldown(self, cooldown):
        self.cooldown = cooldown

        return self

    def set_target_number(self, target_number):
        self.target_number = target_number

        return self

    def set_damage(self, damage_dice):
        self.damage_dice = damage_dice

        return self

    def set_MP_cost(self, MP_cost):
        self.MP_cost = MP_cost

        return self

    def get_damage_range(self):
        return Dice.range(self.damage_dice)

    def get_hit_chance_percent(self):
        return int(self.hit_chance * 100)

    def get_combat_summary(self):
        min_damage, max_damage = self.get_damage_range()
        return "MP %s, hit %s%%, damage %s-%s, cooldown %s turn%s" % (
            self.MP_cost,
            self.get_hit_chance_percent(),
            min_damage,
            max_damage,
            self.cooldown,
            "" if self.cooldown == 1 else "s"
        )

    def _cancel_turn(self, game_description):
        if hasattr(game_description, 'should_update_turn'):
            game_description.should_update_turn = False

    def _target_label(self, target):
        return target.name

    def _target_status(self, target):
        if target.current_room is not None and target in target.current_room.enemies:
            return "%s: %s (HP %s/%s)" % (
                target.current_room.enemies.index(target),
                target.name,
                target.current_HP,
                target.max_HP
            )
        return "%s (HP %s/%s)" % (
            target.name,
            target.current_HP,
            target.max_HP
        )

    def _say_available_targets(self, room):
        if len(room.enemies) == 0:
            say("There are no enemies here.")
            return
        say("Choose a target:")
        for i, enemy in enumerate(room.enemies):
            say("%s: %s (HP %s/%s)" % (
                i,
                enemy.name,
                enemy.current_HP,
                enemy.max_HP
            ))

    def _resolve_target_by_name(self, room, params):
        exact_matches = []
        prefix_matches = []
        target_name = params.lower()
        for enemy in room.enemies:
            enemy_name = enemy.name.lower()
            if target_name == enemy_name:
                exact_matches.append(enemy)
            elif enemy_name.startswith(target_name):
                prefix_matches.append(enemy)
        if len(exact_matches) == 1:
            return exact_matches[0]
        if len(exact_matches) > 1:
            say("Target name is ambiguous. Use the enemy index.")
            return None
        if len(prefix_matches) == 1:
            return prefix_matches[0]
        if len(prefix_matches) > 1:
            say("Target name is ambiguous. Use the enemy index.")
            return None
        say("No target identified.")
        return None

    def _resolve_targets(self, game_description, params):
        room = game_description.current_room
        params = params.strip()
        if len(room.enemies) == 0:
            say("There are no enemies here.")
            return []
        if self.target_number == -1:
            return list(room.enemies)
        if params == "":
            self._say_available_targets(room)
            return []
        if params.isdigit():
            target_index = int(params)
            if target_index >= 0 and target_index < len(room.enemies):
                return [room.enemies[target_index]]
            say("No enemy has index %s." % target_index)
            self._say_available_targets(room)
            return []
        target = self._resolve_target_by_name(room, params)
        if target is None:
            return []
        return [target]

    def cast(self, caster, game_description, params):
        params = params.strip()
        cooldown = caster.get_spell_cooldown(self)
        if cooldown > 0:
            say('"' + self.name + '" is cooling down for ' + str(cooldown) + ' more turn(s).')
            self._cancel_turn(game_description)
            return

        targets = []
        if self.spell_type == SpellType.Attack:
            targets = self._resolve_targets(game_description, params)
            if len(targets) == 0:
                self._cancel_turn(game_description)
                return

        if not game_description.player.use_MP(self.MP_cost):
            say("Not enough MP to cast \"" + self.name + "\".")
            self._cancel_turn(game_description)
            return

        say('Casting spell "' + self.name + '"')
        say("Hit chance: %s%%. Damage: %s-%s." % (
            self.get_hit_chance_percent(),
            self.get_damage_range()[0],
            self.get_damage_range()[1]
        ))

        if self.spell_type == SpellType.Attack:
            for e in targets:
                say("Target: " + self._target_status(e))
                self.description.add_tag("target", [self._target_label(e)])
                say(self.description)
                damage = Dice.parse(self.damage_dice)
                e.receive_damage(damage, caster)

        caster.start_spell_cooldown(self)

    def get_description(self):
        self.description.add_tag("target", "its target")
        say(e.description)
