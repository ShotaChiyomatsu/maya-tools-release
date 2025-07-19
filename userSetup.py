import sys
sys.dont_write_bytecode = True

import maya.utils
from importlib import *
from config import menu as menu
reload(menu)
maya.utils.executeDeferred(menu.main)