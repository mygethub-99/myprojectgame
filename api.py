import logging
#debug=True
import endpoints
from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from models import User, Game, NewGameForm, Inventory
from models import StringMessage, GameForm, InventoryForm, StringMessage1
from models import NewInventList, checkInventory, StringMessageCraftForm
from utils import get_by_urlsafe, check_winner, check_full
from dict_list import items, craft, commands, defaults, crafty

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
NEW_INVENT_LIST = endpoints.ResourceContainer(NewInventList)
INVENT_CHECK = endpoints.ResourceContainer(checkInventory)

#GET_GAME_REQUEST = endpoints.ResourceContainer(
        #urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1), email=messages.StringField(2), wins=messages.StringField(3))
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
        wins = defaults['wins']
        user = User(name=request.user_name, email=request.email, wins = wins)
        #user.put() sends the user info that is ndb
        user.put()
        return StringMessage1(message='User {} created!'.format(
                request.user_name))

        
        #This just returns a message for response at bottom of API
        #screen.
    
   

#Need to check it there is already one for this player!!!!!!!!!!!
    @endpoints.method(request_message= NEW_INVENT_LIST, response_message=InventoryForm, path='inventory', http_method='POST', name='getInventory')
    def _doInventory(self, request):
       
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')
        
        invent= Inventory(name=user.name, user = user.key, flint = items.get("flint"), grass=items.get("grass"), boulder=items.get("boulder"), hay = items.get("hay"), tree = items.get("tree"), sapling = items.get("sapling"))

        invent.put()
        return self._copyInvenToForm(invent)
   
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
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        invenlist = self._inventlist(request)
        try:
            game = Game.new_game(user.key)
        except ValueError:
            raise endpoints.BadRequestException('Maximum must be greater '
                                                'than minimum!')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        #taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Prepare to test your survival skills!')

        #if game.attempts_remaining < 1:
            #game.end_game(False)
            #return game.to_form(msg + ' Game over!')
        #else:
            #game.put()i
            #return game.to_form(msg)


    #Pulls a property value of inventory.
    @endpoints.method(request_message=INVENT_CHECK,
                      response_message=StringMessage,
                      path='invencheck',
                      #This is the name that appears in the api
                      name='check_items',
                      http_method='POST')
    def checkInventory(self, request):
        # Take the input user name and pulls the user info from User Class
        username = User.query(User.name == request.user_name).get()
        #Pulls inventory list from Inventory class = user key.
        chklist = Inventory.query( Inventory.user == username.key).get()
        if not chklist:
            raise endpoints.NotFoundException(
                    'This user does not have any Inventory')
        #Returns checkInventory message
        if username.key == chklist.user:
            itemname = request.item_name
            value = getattr( chklist, itemname)
            placeholder = value
        #itemlist =(" You have {}  of {}".format(itemcount, itemname))
            return StringMessage(message='You have {} {} '.format(
                placeholder, itemname))


    #Used by NewGame to check if old inventory list belongs to user deletes it.
    def _inventlist(self, request):
       
        user = User.query(User.name == request.user_name).get()
        check_invent = Inventory.query(Inventory.name == request.user_name).get()
        
        #Deletes the inventory list and throw message.    
        if check_invent:
            check_invent.key.delete()
            
            raise endpoints.NotFoundException(
                    'User Already has Inventory List. Inventory has been deleted! Try Creating the game again please')

        invent= Inventory(name = user.name, user = user.key, flint = items.get("flint"), grass=items.get("grass"), boulder=items.get("boulder"), hay = items.get("hay"), tree = items.get("tree"), sapling = items.get("sapling"))
        invent.put()
        

    @endpoints.method(message_types.VoidMessage, StringMessage,
            path='howtocraft',
            http_method='GET', name='HowToCraft')
    def howtoCraft(self, request):
        message = crafty
        return StringMessage(message = message)

        
    # Not user this yet memcache yet. 
    @endpoints.method(response_message=StringMessage,
                      path='inventory/check',
                      name='see_what_is_in_Inventory',
                      http_method='GET')
    def pull_inventory(self, request):
        """Get the cached inventory list"""
        return StringMessage(message=memcache.get(MEMCACHE_INVENT_CHECK) or '')  

    @staticmethod
    def _cache_invent():
        """Populates memcache with the inventory list"""
        inventlist= Inventory.query.fetch()
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
