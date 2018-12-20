import rpglib
import importutils

importutils.addpath(__file__, 'gamedescription')
from gamedescription import game_description

rpglib.start(game_description)
