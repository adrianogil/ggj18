import rpglib
from rpglib import Enemy

from grammar import SimpleGrammar

def set_random_enemy(room):
    room.set_enemies([rpglib.get_random_enemy()])

def get_description():
    rpglib.Room.items = rpglib.Bag()

    starting_room = rpglib.Room("""
    You are in a dark room.
    """).set_name('Room 01')

    corridor = starting_room.north = rpglib.Room("""
    You are in a big corridor that smells odly.
    """).set_name('Room 02')
    corridor.set_player_enter_callback(set_random_enemy)

    dark_lab = corridor.north = rpglib.Room("""
    You are in a dark laboratory.
    """).set_name('Room 03')
    dark_lab.set_player_enter_callback(set_random_enemy)

    green_room = corridor.east = rpglib.Room("""
    You are in a green rooom.
    """).set_name('Room 04')
    green_room.set_player_enter_callback(set_random_enemy)

    mallet = rpglib.Item('rusty mallet', 'mallet')
    corridor.items = rpglib.Bag({mallet,})

    game_description = rpglib.GameDescription()
    game_description.current_room = starting_room
    game_description.player.inventory = rpglib.Bag() # Empty inventory

    game_description.defined_enemies = [
        ###############################################################################
        Enemy("Kobold")
            .setHP('2d4+1')
            .add_attack(SimpleGrammar()
                .set_text("#attack#")
                .add_tag("attack", [
                    "#name# is attacking #target# with its claws"
                    ]),
                '1d4'),
        ###############################################################################
        Enemy("Baby Werewolf")
            .setHP('2d6+3')
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
                " a furred and well-muscled humanoid body topped by a ravening wolf’s head."),
        ###############################################################################
        Enemy("Goblin")
            .setHP(4)
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
        ###############################################################################
    ]

    return game_description