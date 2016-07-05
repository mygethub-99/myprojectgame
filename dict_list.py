from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.api import memcache

from models import Inventory, User, Game
import time



#Commands to see options, inventory, and craft itmes.
commands = {
                "i" : "see inventory",
                "c" : "see crafting options",
                "craft [item]" : "craft something from inventory items",
           }

#an inventory of items
items = {
            "flint" : 50,

            "grass" : 100,
            "hay" : 0,

            "tree" : 100,
            "log" : 0,

            "sapling" : 100,
            "twig" : 0,

            "boulder" : 30,
            "rock" : 0,

            "pickaxe" : 0,
            "axe" : 0,

            "firepit" : 0,
            "tent" : 0,

            "torch" : 0,
        }

# Items needed to make an item for survival.
craft = {
            "hay" : { "grass" : 1 },
            "twig" : { "sapling" : 1 },
            "log" : { "axe" : 1, "tree" : 1 },
            "axe" : { "twig" : 3, "flint" : 1 },
            "tent" : { "twig" : 10, "hay" : 15 },
            "firepit" : { "boulder" : 5, "log" : 3, "twig" : 1, "torch" : 1 },
            "torch" : { "flint" : 1, "grass" : 1, "twig" : 1 },
            "pickaxe" : { "flint" : 2, "twig" : 1 }
        }

#Provides how to craft strings for HowToCraft endpoint in api.py        
hay = "To make hay it takes 1 grass"
twig = "To make twig it takes 1 sapling"
log = "To make a log it takes 1 axe and 1 tree"
axe = "To make a axe it takes 3 twigs and 1 flint"
tent = "To make a tent it takes 10 twigs, 15 hay"
firepit = "To make a firepit it takes 5 boulder, 3 log, 1 twig, 1 torch"
torch = "To make a torch it takes 1 flint, 1 grass, 1 twig"
pickaxe = "To make a pickaxe it takes 2 flint, 1 twig"
crafty =[hay, twig, log, axe, tent, torch, firepit, pickaxe]

defaults = {
	"wins" : 0,
	"total_played": 0
}

def gamecheck (ingamecheck):
    if ingamecheck.difficulty == 2:
        if ((int(time.time())-ingamecheck.timer)/60) == 7:
            setattr(ingamecheck, "timeout", True)
            ingamecheck.put()
    if ingamecheck.difficulty == 3:
        if ((int(time.time())-ingamecheck.timer)/60) == 1:
            setattr(ingamecheck, "timeout", True)
            ingamecheck.put()
    return

