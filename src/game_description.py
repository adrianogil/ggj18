import rpglib

def get_description():
    rpglib.Room.items = rpglib.Bag()

    starting_room = rpglib.Room("""
    You are in a dark room.
    """)

    valley = starting_room.north = rpglib.Room("""
    You are in a beautiful valley.
    """)

    magic_forest = valley.north = rpglib.Room("""
    You are in a enchanted forest where magic grows wildly.
    """)

    mallet = rpglib.Item('rusty mallet', 'mallet')
    valley.items = rpglib.Bag({mallet,})

    game_description = rpglib.GameDescription()
    game_description.current_room = starting_room
    game_description.player.inventory = rpglib.Bag() # Empty inventory

    return game_description