from models import Inventory, User
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
        delay=10
        while (delay >=0):
            delay -=1
            time.sleep(1)
        print "number 2 worked"
        game_over(ingamecheck)
    if ingamecheck.difficulty == 3:
        delay=10
        while(delay >=0):
            delay -=1
            time.sleep(1)
        print "number 3 worked"
        game_over(ingamecheck)

 
#def loadInventory(invent):
    #user = User.query(User.name == request.user_name).get()
    #if not user:
        #raise endpoints.NotFoundException('A User with that name does not exist!')
    #invent= Inventory(user = user.key, flint = items.get("flint"), grass=items.get("grass"), boulder=items.get("boulder"), hay = items.get("hay"), tree=items.get("tree"), sapling=items.get("sapling", twig=items.get("twig"), rock=items.get("rock"), pickaxe=items.get("pickaxe"))
    #return invent

    #Inventory = type("Inventory", (object,), dict())
    #invent = Inventory()

    #for key, val in items.items():
        #setattr(invent, key, val)
        #return invent

#inven= Inventory(flint = items.get("flint"), grass=items.get("grass"), boulder=items.get("boulder"), hay = items.get("hay"))
