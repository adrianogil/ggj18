import ggj18.rpglib.rpglib as rpglib
from ggj18.rpglib.rpglib import Enemy, Spell, SpellType, Creature, Bag, Room, Item, GameDescription
from ggj18.rpglib.rpglib import say

from ggj18.rpglib.grammar import SimpleGrammar
from ggj18.rpglib.grammar import SimpleGrammar as SG

from ggj18.rpglib.dice import Dice
Dp = Dice.parse

import ggj18.rpglib.utils as utils

import random



def set_random_enemy(room):
    room.set_enemies([rpglib.get_random_enemy()])


def get_description():
    Room.items = Bag()

    starting_room = Room("""
    You are in a dark room.
    """)\
    .set_name('Room 01')

    corridor = starting_room.north = Room("""
    You are in a big corridor that smells odly.
    """)\
    .set_name('Room 02')\
    .set_player_enter_callback(set_random_enemy)

    dark_lab = corridor.north = Room("""
    You are in a dark laboratory.
    """)\
    .set_name('Room 03')\
    .set_player_enter_callback(set_random_enemy)

    green_room = corridor.east = Room("""
    You are in a green rooom.
    """)\
    .set_name('Room 04')\
    .set_player_enter_callback(set_random_enemy)

    rnd_room2 = dark_lab.west = Room(SG().set_text("""
    You are in #place_description#.
    """).at("place_description", [
        "an alien place that can't be really explained",
        "a very strange abandoned bar",
        "a mistic and dark temple",
        "an old and dirty cave"
    ]))\
    .set_name('Room 05')\
    .set_player_enter_callback(set_random_enemy)

    rnd_room = green_room.north = Room(SG().set_text("""
    You are in #place_description#.
    """).at("place_description", [
        "an alien place that can't be really explained",
        "a very strange abandoned bar",
        "a mistic and dark temple",
        "an old and dirty cave"
    ]))\
    .set_name('Room 06')\
    .set_player_enter_callback(set_random_enemy)

    healing_room = rnd_room2.west = Room(SG().set_text("""
    You are in #place_description#.
    """).at("place_description", [
        "an sacred place that make you feels better",
        "a very strange abandoned bar with a warm energy",
        "a mistic and dark temple with a healing energy",
        "an old and dirty cave with a warm energy"
    ]))\
    .set_name('Room 07')

    mallet = Item('rusty mallet', 'mallet')
    corridor.items = Bag({mallet,})

    def generate_potion_action(cure_value):
        def cure_action(item, rpg_game_description):
            cHp = rpg_game_description.player.current_HP
            cured_points = Dp(cure_value)
            cHp = cHp + cured_points
            say(utils.capitalize(item.name) + ' cured ' + str(cured_points) + ' HP points!')
            if cHp > rpg_game_description.player.max_HP:
                rpg_game_description.player.current_HP = rpg_game_description.player.max_HP
            else:
                rpg_game_description.player.current_HP = cHp
        return cure_action

    def generate_elixir_action(cure_value):
        def elixir_action(item, rpg_game_description):
            cMp = rpg_game_description.player.current_MP
            cured_points = Dp(cure_value)
            cMp = cMp + cured_points
            say(utils.capitalize(item.name) + ' cured ' + str(cured_points) + ' MP points!')
            if cMp > rpg_game_description.player.max_MP:
                rpg_game_description.player.current_MP = rpg_game_description.player.max_MP
            else:
                rpg_game_description.player.current_MP = cMp
        return elixir_action

    def new_red_potion():
        red_potion = Item('red potion', 'potion')
        red_potion.is_consumable = True
        red_potion.on_consume = generate_potion_action('2d6+2')
        return red_potion

    def new_blue_elixir():
        blue_elixir = Item('blue elixir', 'elixir')
        blue_elixir.is_consumable = True
        blue_elixir.on_consume = generate_elixir_action('2d4+3')
        return blue_elixir

    red_potion = new_red_potion()
    blue_elixir = new_blue_elixir()

    game_description = GameDescription()
    game_description.starting_room = starting_room
    game_description.current_room = starting_room
    game_description.player.inventory = Bag() # Empty inventory

    game_description.player.set_max_HP(Dice.parse('6d4+1d10+5'))
    game_description.player.set_max_MP(Dice.parse('3d7+2d10+3'))
    game_description.player.name = 'Wizard Owl'


    def healing_action(room):
        cHp = game_description.player.current_HP
        cured_points = Dp('2d5+3')
        cHp = cHp + cured_points
        say('The healing energy cured ' + str(cured_points) + ' HP points!')
        if cHp > game_description.player.max_HP:
            game_description.player.current_HP = game_description.player.max_HP
        else:
            game_description.player.current_HP = cHp

    def add_room_loot(room):
        if room.loot_checked:
            return
        room.loot_checked = True
        if room.loot_chance <= 0 or random.randint(1, 100) > room.loot_chance:
            return
        loot = random.choice([new_red_potion, new_blue_elixir])()
        room.items.add(loot)
        say("You notice a %s tucked away in the room." % loot.name)

    def run_room_event(room):
        if room.room_event is None or room.room_event_done:
            return
        room.room_event_done = True

        if room.room_event == "trap":
            damage = Dp('1d6+1')
            say("A hidden trap snaps shut for %s damage." % damage)
            game_description.player.receive_damage(damage, room)
        elif room.room_event == "shrine":
            cured_points = Dp('1d6+2')
            new_hp = game_description.player.current_HP + cured_points
            game_description.player.current_HP = min(new_hp, game_description.player.max_HP)
            say("A quiet shrine restores %s HP." % cured_points)
        elif room.room_event == "merchant":
            room.items.add(new_red_potion())
            say("A wandering merchant has moved on, leaving a red potion behind.")
        elif room.room_event == "ambush":
            say("Shapes rush out from cover.")
            set_random_enemy(room)

    def varied_room_action(room):
        run_room_event(room)
        add_room_loot(room)
        enemy_chance = min(85, room.danger * 20)
        if room.danger > 0 and len(room.enemies) == 0 and random.randint(1, 100) <= enemy_chance:
            set_random_enemy(room)

    def healing_room_action(room):
        varied_room_action(room)
        healing_action(room)

    def make_room(name, template):
        return Room(template["description"])\
            .set_name(name)\
            .set_tags(template["biome"], template["danger"], template["loot_chance"])\
            .set_room_event(template.get("event"))\
            .set_player_enter_callback(varied_room_action)

    starting_room.set_tags("dungeon", 0, 10)
    corridor.set_tags("corridor", 1, 20)\
        .set_room_event("merchant")\
        .set_player_enter_callback(varied_room_action)
    dark_lab.set_tags("laboratory", 2, 35)\
        .set_room_event("trap")\
        .set_player_enter_callback(varied_room_action)
    green_room.set_tags("overgrown", 1, 25)\
        .set_player_enter_callback(varied_room_action)
    rnd_room2.set_tags("void", 3, 40)\
        .set_room_event("ambush")\
        .set_player_enter_callback(varied_room_action)
    rnd_room.set_tags("ruins", 2, 35)\
        .set_room_event("trap")\
        .set_player_enter_callback(varied_room_action)
    healing_room.set_tags("sanctuary", 0, 45)\
        .set_room_event("shrine")\
        .set_player_enter_callback(healing_room_action)

    room_templates = [
        {
            "description": "You are in a flooded archive. Water laps against shelves of ruined books.",
            "biome": "flooded",
            "danger": 1,
            "loot_chance": 35,
            "event": "trap"
        },
        {
            "description": "You are in a crystal grotto where pale light crawls through the walls.",
            "biome": "crystal",
            "danger": 1,
            "loot_chance": 45,
            "event": "shrine"
        },
        {
            "description": "You are in a collapsed guard post with broken spears underfoot.",
            "biome": "barracks",
            "danger": 2,
            "loot_chance": 30,
            "event": "ambush"
        },
        {
            "description": "You are in a fungal garden. Soft caps glow between cracked tiles.",
            "biome": "fungal",
            "danger": 1,
            "loot_chance": 40,
            "event": "merchant"
        },
        {
            "description": "You are in a scorched forge. Cold anvils surround a dead furnace.",
            "biome": "forge",
            "danger": 2,
            "loot_chance": 25,
            "event": "trap"
        },
        {
            "description": "You are in a mirror hall. Your reflection arrives a heartbeat late.",
            "biome": "arcane",
            "danger": 3,
            "loot_chance": 50,
            "event": "ambush"
        },
        {
            "description": "You are in a mossy cistern. Something below the surface keeps circling.",
            "biome": "cistern",
            "danger": 2,
            "loot_chance": 30,
            "event": "trap"
        },
        {
            "description": "You are in a moonlit chapel with silver dust on the altar.",
            "biome": "chapel",
            "danger": 0,
            "loot_chance": 55,
            "event": "shrine"
        },
        {
            "description": "You are in a narrow root tunnel. The walls pulse like sleeping lungs.",
            "biome": "root",
            "danger": 2,
            "loot_chance": 20,
            "event": "ambush"
        },
        {
            "description": "You are in a ruined market stall packed with moldy travel gear.",
            "biome": "market",
            "danger": 1,
            "loot_chance": 60,
            "event": "merchant"
        },
        {
            "description": "You are in a wind-cut overlook above a black underground lake.",
            "biome": "cliff",
            "danger": 1,
            "loot_chance": 25,
            "event": "trap"
        },
        {
            "description": "You are in a bone gallery where old trophies hang from copper wire.",
            "biome": "ossuary",
            "danger": 3,
            "loot_chance": 45,
            "event": "ambush"
        },
        {
            "description": "You are in an ash nursery with tiny handprints on every wall.",
            "biome": "ash",
            "danger": 2,
            "loot_chance": 35,
            "event": "shrine"
        },
        {
            "description": "You are in a silent observatory pointed at a stone ceiling.",
            "biome": "observatory",
            "danger": 1,
            "loot_chance": 50,
            "event": "merchant"
        }
    ]

    room08 = dark_lab.north = make_room("Room 08", room_templates[0])
    room09 = room08.east = make_room("Room 09", room_templates[1])
    room10 = room09.north = make_room("Room 10", room_templates[2])
    room11 = room10.west = make_room("Room 11", room_templates[3])
    room12 = room11.south = make_room("Room 12", room_templates[4])

    room13 = green_room.east = make_room("Room 13", room_templates[5])
    room14 = room13.north = make_room("Room 14", room_templates[6])
    room15 = room14.east = make_room("Room 15", room_templates[7])
    room16 = room15.south = make_room("Room 16", room_templates[8])

    room17 = healing_room.north = make_room("Room 17", room_templates[9])
    room18 = room17.west = make_room("Room 18", room_templates[10])
    room19 = room18.north = make_room("Room 19", room_templates[11])
    room20 = room19.east = make_room("Room 20", room_templates[12])
    room20.south = make_room("Room 21", room_templates[13])

    game_description.defined_enemies = [
        ###############################################################################
        Enemy("Kobold")
            .setHP('2d4+1')
            .set_granted_XP(Dice.parse('3d10'))
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is attacking #target# with its claws"
                    ]),
                '1d4')
            .set_loot({"coins": Dp("2d10"), "items" : [red_potion]}),
        ###############################################################################
        Enemy("Baby Werewolf")
            .setHP('2d6+3')
            .set_granted_XP(Dice.parse('5d4+1d10+3d6+10'))
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is attacking #target# with its claws"
                    ]),
                '1d4+1')
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is biting #target# violently"
                    ]),
                '2d4')
            .set_description("A werewolf is a savage predator in a terrifying hybrid form," + 
                " a furred and well-muscled humanoid body topped by a ravening wolf’s head.")
            .set_loot({"coins": Dp("3d10+5"), "items" : [blue_elixir]}),
        ###############################################################################
        Enemy("Goblin")
            .setHP(4)
            .set_granted_XP(Dice.parse('2d4'))
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is attacking #target# with its small sword"
                    ]),
                '1d4+1')
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is attacking #target# with its spear"
                    ]),
                '1d4')
            .set_loot({"coins": Dp("2d10"), "items" : [red_potion]}),
        Enemy("Baby Demon")
            .setHP('2d6')
            .set_granted_XP(Dice.parse('2d4+2d6'))
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is attacking #target# with its small claws"
                    ]),
                '1d6+1')
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is attacking #target# with its teeth"
                    ]),
                '2d4')
            .set_loot({"coins": Dp("2d10"), "items" : [blue_elixir]})
        ###############################################################################
    ]

    defined_spells = {
        "Magic missiles" : Spell("Magic missiles", 
                        SimpleGrammar().set_text("A missile of magical energy darts forth from your fingertip and strikes #target#"),
                         SpellType.Attack)
                    .set_damage('1d4+1')
                    .set_MP_cost(1),
        "Fireball" : Spell("Fireball", 
                        SimpleGrammar().set_text("An explosion of flame that detonates with a low roar"),
                         SpellType.Attack)
                    .set_damage('3d4+4')
                    .set_MP_cost(5)
                    .set_target_number(-1),
        "Fire Storm" : Spell("Fire Storm", 
                        SimpleGrammar().set_text("The whole area is shot through with sheets of roaring flame"),
                         SpellType.Attack)
                    .set_damage('4d4+5')
                    .set_MP_cost(6)
                    .set_target_number(-1),
        "Acid Arrow" : Spell("Acid Arrow", 
                        SimpleGrammar().set_text("A magical arrow of acid springs from your hand and speeds to #target#"),
                         SpellType.Attack)
                    .set_damage('2d4+2')
                    .set_MP_cost(2)
                    .set_target_number(-1),
        "Frost Lance" : Spell("Frost Lance",
                        SimpleGrammar().set_text("A spear of icy wind streaks toward #target#, riming the air with frost"),
                         SpellType.Attack)
                    .set_damage('2d6+2')
                    .set_MP_cost(3),
        "Lightning Bolt" : Spell("Lightning Bolt",
                        SimpleGrammar().set_text("A crackling bolt of lightning arcs toward #target#"),
                         SpellType.Attack)
                    .set_damage('3d6')
                    .set_MP_cost(4),
        "Shadow Spike" : Spell("Shadow Spike",
                        SimpleGrammar().set_text("A jagged spike of shadow erupts beneath #target#"),
                         SpellType.Attack)
                    .set_damage('2d8')
                    .set_MP_cost(4),
        "Thunderclap" : Spell("Thunderclap",
                        SimpleGrammar().set_text("A concussive boom slams into #target#"),
                         SpellType.Attack)
                    .set_damage('3d4+3')
                    .set_MP_cost(3),
        "Flame Lash" : Spell("Flame Lash",
                        SimpleGrammar().set_text("A whip of flame snaps across #target#"),
                         SpellType.Attack)
                    .set_damage('2d6+1')
                    .set_MP_cost(3),
        "Stone Shards" : Spell("Stone Shards",
                        SimpleGrammar().set_text("Razor-edged stone shards swirl into #target#"),
                         SpellType.Attack)
                    .set_damage('2d6')
                    .set_MP_cost(3),
        "Ice Nova" : Spell("Ice Nova",
                        SimpleGrammar().set_text("A burst of crystalline ice explodes around #target#"),
                         SpellType.Attack)
                    .set_damage('3d4+2')
                    .set_MP_cost(4),
        "Arcane Pierce" : Spell("Arcane Pierce",
                        SimpleGrammar().set_text("A needle of pure arcane force pierces #target#"),
                         SpellType.Attack)
                    .set_damage('2d8+1')
                    .set_MP_cost(4),
        "Venom Burst" : Spell("Venom Burst",
                        SimpleGrammar().set_text("A vile burst of venom splashes over #target#"),
                         SpellType.Attack)
                    .set_damage('2d6+2')
                    .set_MP_cost(3),
        "Solar Flare" : Spell("Solar Flare",
                        SimpleGrammar().set_text("A blinding flare of sunlight scorches #target#"),
                         SpellType.Attack)
                    .set_damage('3d6+1')
                    .set_MP_cost(5),
        "Grave Chill" : Spell("Grave Chill",
                        SimpleGrammar().set_text("A necrotic chill clings to #target#"),
                         SpellType.Attack)
                    .set_damage('2d6+3')
                    .set_MP_cost(3),

    }
    game_description.defined_spells = defined_spells
    game_description.player.defined_spells = defined_spells

    learned_spells = [
        defined_spells["Magic missiles"],
        defined_spells["Fireball"],
    ]
    game_description.player.learned_spells = learned_spells

    defined_creatures = {
        "Little demon" : Creature("Little demon", 4)
                        .setHP(5)
                        .set_cast_time(10)
                        .set_damage_dice('1d4')
    }
    game_description.player.defined_creatures = defined_creatures

    game_description.player.learned_invokable_creatures = [
            defined_creatures["Little demon"]
    ]


    return game_description
