from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from google.appengine.ext.db import Key
from google.appengine.api import background_thread
from models import Inventory, User, Game
import time
import threading


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
pickaxe = "To make a pickaxe it takes 2 flint, 1 twig"
crafty =[hay, twig, log, axe, tent, firepit, pickaxe]



defaults = {
	"wins" : 10,
	"total_played": 0
}


def countdown(ingamecheck):
    if ingamecheck.difficulty < 2:
        print "nothing needed"
    if ingamecheck.difficulty == 2:
        delay=20
        while (delay >=0):
            delay -=1
            time.sleep(1)
        print "number 2 worked"
        setattr(ingamecheck, "game_over", True)
        ingamecheck.put()
    if ingamecheck.difficulty == 3:
        delay=30
        while(delay >=0):
            delay -=1
            time.sleep(1)
        print "number 3 worked"
        return game_over(ingamecheck)

def delayer(ingamecheck):
    if ingamecheck.difficulty < 2:
        print "nothing needed"
    if ingamecheck.difficulty == 2:
        delay=60
        while (delay >=0):
            delay -=1
            time.sleep(1)
        setattr(ingamecheck, "game_over", True)
        ingamecheck.put()
            
    if ingamecheck.difficulty == 3:
        delay=30
        while(delay >=0):
            delay -=1
            time.sleep(1)
        setattr(ingamecheck, "game_over", True)
        ingamecheck.put()

def gamecheck (ingamecheck):
    if ingamecheck.difficulty == 2:
        if ((int(time.time())-ingamecheck.timer)/60)/2 == 1:
            setattr(ingamecheck, "game_over", True)
            setattr(ingamecheck, "timeout", True)
            ingamecheck.put()
    if ingamecheck.difficulty == 3:
        if ((int(time.time())-ingamecheck.timer)/60)/2 == 2:
            setattr(ingamecheck, "game_over", True)
            setattr(ingamecheck, "timeout", True)
            ingamecheck.put()
    return

