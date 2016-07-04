import logging
import time
#debug=True
import endpoints
from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from google.appengine.ext.db import Key
from models import User, Game, NewGameForm, Inventory
from models import StringMessage, GameForm, StringMessage1
from models import checkInventory, StringMessageCraftForm
from models import CraftForm, CraftItem, cancel_game
from utils import get_by_urlsafe, check_winner, check_full
from dict_list import items, craft, commands, defaults, crafty
from dict_list import gamecheck

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s',
                    )




NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
INVENT_CHECK = endpoints.ResourceContainer(checkInventory)
CRAFT_ITEM = endpoints.ResourceContainer(CraftItem)
CANCELED_GAME = endpoints.ResourceContainer(cancel_game)
GAME_HISTORY = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1))

#GET_GAME_REQUEST = endpoints.ResourceContainer(
        #urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1), email=messages.StringField(2))

MEMCACHE_INVENT_CHECK = 'INVENT_CHECK'
#Got to figure out how to pass the command message output.
#MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'



@endpoints.api(name='survive', version='v1')
class SurviveAPI(remote.Service):
    """Game API"""


    
     
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage1,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        #By adding wins, it added it to the create_user input #api page.
        #wins = defaults['wins']
        user = User(name=request.user_name, email=request.email)
        #user.put() sends the user info that is ndb
        user.put()
        return StringMessage1(message='User {} created!'.format(
                request.user_name))

       
    #This is not sending the output to the form.
    #Since I added the inventory create function to the new
    #game function, this form may be going away. Sorry!
    def _copyInvenToForm(self,inven):
        pf = InventoryForm()
        for field in pf.all_fields():
            if hasattr(inven, field.name):
                setattr(pf, field.name, getattr(inven, field.name))
        pf.check_initialized()
        return pf
        
    
    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""

        user=User.query(User.name==request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        #Check to see if use is already in a live game.
        ingamecheck=Game.query(Game.user==user.key).get()
        setdiff=request.how_hard
        #Test to see if a game entity actually exist.
        if hasattr(ingamecheck, "user")==True:
            if ingamecheck.game_over==False:
                raise endpoints.ConflictException('Only one active game per user is allowed')
            else:
                invenlist=self._inventlist(request)
                game=Game.new_game(user.key, setdiff)
                return game.to_form('Prepare to test your survival skills!')
        else:
            invenlist=self._inventlist(request)
            game=Game.new_game(user.key, setdiff)
            return game.to_form('Prepare to test your survival skills!')

    #Needs to increment User total_played.
    def game_over(self, ingamecheck):
        setattr(ingamecheck, "game_over", True)
        ingamecheck.put()
        raise endpoints.ConflictException('You have run out of time. Game Over!')


    @endpoints.method(request_message=CANCELED_GAME,
                      response_message=StringMessage1,
                      path='cancel',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """Cancels game in progress"""
        user=User.query(User.name==request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        #Check to see if use is in a live game.
        ingamecheck=Game.query(Game.user==user.key).get()
        if hasattr(ingamecheck, "user")==True:
            if getattr(ingamecheck, "game_over")==False and getattr(ingamecheck, "canceled_game")==False:
                setattr(ingamecheck, "canceled_game", True)
                setattr(ingamecheck, "game_over", True)
                ingamecheck.put()
                return StringMessage1(message='User {} has canceled the game. Play again soon!!!'.format(request.user_name))
            else:
                return StringMessage1(message='User {} is not in a active game. Game cant be canceled'.format(request.user_name))
        else:
            raise endpoints.NotFoundException(
                    'User {} does not have any games to cancel!'.format(request.user_name))

    
    #Function to re-populate the copycraft dict with inventory values.        
    def invenOfCraft(self, copycraft, inventory_items):
        for w in copycraft:
            copycraft[w]=getattr(inventory_items, w)
        return copycraft

    def dude(self, ingamecheck):
        trigger = 2
        if trigger < 2:
            raise endpoints.ConflictException('User is not in an active game. Please create a new game.')
        if trigger == 2:
            delay=60
            time.sleep(60)
            setattr(ingamecheck, "game_over", True)
            ingamecheck.put()
            
        if trigger == 3:
            delay=60
            while(delay >=0):
                delay -=1
                time.sleep(1)
            setattr(ingamecheck, "game_over", True)
            ingamecheck.put()

    
    @endpoints.method(request_message=CRAFT_ITEM,
                      response_message=StringMessage1,
                      path='craft',
                      name='craft_item', 
                      http_method='POST')
    def craftItemNew(self, request):
        """Craft an item"""
        user=User.query(User.name==request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        ingamecheck=Game.query(Game.user==user.key).get()
        if not ingamecheck:
            raise endpoints.NotFoundException('User is not in a game. Please create a new game for this user.')
        #Check for an active game.This will not work!
        if ingamecheck.timeout == True:
            raise endpoints.ConflictException('Player has run out of time and did not survive! Start a new game.')
        if ingamecheck.game_over==True:
            raise endpoints.ConflictException('User is not in an active game. Please create a new game.')
        #Starts the game timer.
        if ingamecheck.game_started == False:
            t1=int(time.time())
            gamediff=getattr(ingamecheck, "difficulty")
            setattr(ingamecheck, "timer", t1)
            setattr(ingamecheck, "game_started", True)
            ingamecheck.put()
        #Compares timer to current time.
        if ingamecheck.game_started == True:
            if ingamecheck.difficulty > 1:
                gamecheck(ingamecheck)
        # Make a dict of inventory from ndb
        inventory_items=Inventory.query( Inventory.user==user.key).get()
        # Create a dict of what is needed to craft the item     
        takesToCraft=craft.get(request.itemcraft)
        if takesToCraft == None:
            raise endpoints.NotFoundException('Invalid item name.')
        # Make a copy of takesToCraft to re-populate with ndb values.
        copycraft=takesToCraft.copy()
        #Calls a function to populate copycraft with actual inventory values from the Inventory ndb model.
        self.invenOfCraft(copycraft, inventory_items)
        #return of invenOfCraft function.
        inven_ndb=copycraft
        #Compares what is needed to craft an item to what exist in inventory.
        #Determines if required items are present in inventory.
        #Flags True or Fales.
        #Returns message to user if insufficent items in inventory to craft an item.
        canBeMade=True
        for i in craft[request.itemcraft]:
            if craft[request.itemcraft] [i]>inven_ndb[i]:
                canBeMade=False
                return StringMessage1(message='Sorry, item can not be crafted. Takes {}, you only have {}'.format(takesToCraft, inven_ndb))
        if canBeMade==True:
            # Adds 1 to the quantity of a crafted item in ndb model.
            increment=1+getattr(inventory_items, request.itemcraft)
            setattr(inventory_items, request.itemcraft, increment)
            #Decrement inventory items used to craft a new item.
            neededForCraft= takesToCraft.copy()
            for w in neededForCraft:
                if hasattr(inventory_items, w)==True:
                    setattr(inventory_items, w, getattr(inventory_items, w)-neededForCraft[w])
            inventory_items.put()

        #Checks to see if you have survived and won the game.
        if inventory_items.tent>=1 and inventory_items.firepit>=1:
            #gamePull = Game.query( Game.user==user.key).get()
            setattr(ingamecheck, "survived", True)
            setattr(ingamecheck, "game_over", True)
            setattr(user, "wins", 1+getattr(user, "wins"))
            setattr(user, "total_played", 1+getattr(user, "total_played"))
            ingamecheck.put()
            user.put()
            return StringMessage1(message='Congrats {}, you survived! Game over.'.format(inventory_items.name))
        else:
            ingamecheck.history.append(request.itemcraft)
            ingamecheck.put()
            return StringMessage1(message='{} Can be crafted! {}, You have {}'.format(request.itemcraft, takesToCraft, inven_ndb))
        

    #Pulls a property value of inventory.
    @endpoints.method(request_message=INVENT_CHECK,
                      response_message=StringMessage1,
                      path='invencheck',
                      #This is the name that appears in the api
                      name='check_items',
                      http_method='POST')
    def checkInventory(self, request):
        """Used to pull inventory on a item"""
        #Take the input user name and pulls the user info from User Class
        username=User.query(User.name==request.user_name).get()
        #Pulls inventory list from Inventory class = user key.
        chklist=Inventory.query( Inventory.user==username.key).get()
        if not chklist:
            raise endpoints.NotFoundException(
                    'This user does not have any Inventory')
        #Returns checkInventory message
        if username.key==chklist.user:
            itemname=request.item_name
            value=getattr( chklist, itemname)
            placeholder=value
        #itemlist =(" You have {}  of {}".format(itemcount, itemname))
            return StringMessage1(message='You have {} {} '.format(
                value, itemname))

 
    #Used by NewGame to check if old inventory list belongs to user deletes it.
    def _inventlist(self, request):
        user=User.query(User.name==request.user_name).get()
        check_invent=Inventory.query(Inventory.name==request.user_name).get()
        #Deletes the inventory list and throw message.    
        if check_invent:
            check_invent.key.delete()
        invent=Inventory(name=user.name, user=user.key, flint=items.get("flint"), grass=items.get("grass"), boulder=items.get("boulder"), hay=items.get("hay"), tree=items.get("tree"), sapling=items.get("sapling"))
        invent.put()
        

    @endpoints.method(message_types.VoidMessage, StringMessage,
            path='howtocraft',
            http_method='GET', name='HowToCraft')
    def howtoCraft(self, request):
        """Pulls a list of how to craft an item."""
        message=crafty
        return StringMessage(message=message)


    #Display game history.
    @endpoints.method(request_message=GAME_HISTORY,
                      response_message=StringMessage1,
                      path='game/{urlsafe_game_key}',
                      name='game_history',
                      http_method='GET')
    def gameHistory(self, request):
        """Returns the move history of a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        #game=Game.query(Game.ndb.==request.gamekeys).get()
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage1(message=str(game.history))

         
    # Not user this yet memcache yet. 
    @endpoints.method(response_message=StringMessage,
                      path='inventory/check',
                      name='see_what_is_in_Inventory',
                      http_method='GET')
    def pull_inventory(self, request):
        """Get the cached inventory list"""
        return StringMessage(message=memcache.get(MEMCACHE_INVENT_CHECK) or '')  

    @staticmethod
    def _cache_game(self):
        """Populates memcache with copy of Game ndb.Model"""
        copyGame=Game.query( Game.user==username.key).get()
        copyGame=Inventory.query.fetch()
        memcache.set(MEMCACHE_INVENT_CHECK, 'Here is your list of items')
        
        #games = Game.query(Game.game_over == False).fetch()
        #if games:
            #count = len(games)
            #total_attempts_remaining = sum([game.attempts_remaining
                                        #for game in games])
            #average = float(total_attempts_remaining)/count
            #memcache.set(MEMCACHE_MOVES_REMAINING,
                         #'The average moves remaining is {:.2f}'.format(average))
api = endpoints.api_server([SurviveAPI])
