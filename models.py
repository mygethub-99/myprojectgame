import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext import db
import pickle



class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    total_played = ndb.IntegerProperty(default=0)
    score = ndb.IntegerProperty(default=0)

    @property
    def win_percentage(self):
        if self.total_played > 0:
            return float(self.wins)/float(self.total_played)
        else:
            return 0

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins,
                        total_played=self.total_played,
                        win_percentage=self.win_percentage)
    def to_score(self):
        return ScoreForm(name=self.name,
                         score=self.score
                         )


#Response message form for user creation
#Sent by the return StringMessage statement in def create_user
class StringMessage(messages.Message):
    """StringMessage-- outbound (multi) string message"""
    message = messages.StringField(1, repeated = True)


class StringMessage1(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1)


#Upload items list to ndb
class Inventory(ndb.Model):
    flint = ndb.IntegerProperty(default=0)
    grass = ndb.IntegerProperty(default=0)
    hay = ndb.IntegerProperty(default=0)
    log = ndb.IntegerProperty(default=0)
    sapling = ndb.IntegerProperty(default=0)
    twig = ndb.IntegerProperty(default=0)
    boulder = ndb.IntegerProperty(default=0)
    pickaxe = ndb.IntegerProperty(default=0)
    axe = ndb.IntegerProperty(default=0)
    firepit = ndb.IntegerProperty(default=0)
    tent = ndb.IntegerProperty(default=0)
    torch = ndb.IntegerProperty(default=0)
    tree = ndb.IntegerProperty(default=0)
    user = ndb.KeyProperty(required=True, kind='User')
    name = ndb.StringProperty(required=True)


#Input form for the Query the Inventory list by a property, ie boulder.
class checkInventory(messages.Message):
    user_name = messages.StringField(1, required=True)
    item_name = messages.StringField(2, required=True)

class cancel_game(messages.Message):
    """Used to cancel a game in progress"""
    user_name = messages.StringField(1, required=True)


class Game(ndb.Model):
    """Game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    survived = ndb.BooleanProperty(required=True, default=False)
    #history = ndb.PickleProperty(required=True)
    canceled_game = ndb.BooleanProperty(required=True, default=False)
    history=ndb.PickleProperty(required=True)
    game_started = ndb.BooleanProperty(required=True, default=False)
    difficulty = ndb.IntegerProperty(required=True, default=0)
    timeout = ndb.BooleanProperty(required=True, default=False)
    timer = ndb.IntegerProperty(required=True, default=0)
    #target = ndb.IntegerProperty(required=True)
    #attempts_allowed = ndb.IntegerProperty(required=True)
    #attempts_remaining = ndb.IntegerProperty(required=True, default=5)
    #game_over = ndb.BooleanProperty(required=True, default=False)
    #user = ndb.KeyProperty(required=True, kind='User')


    @classmethod
    def new_game(cls, user, setdiff):
        """Creates and returns a new game"""
        #if max < min:
            #raise ValueError('Maximum must be greater than minimum')
        game = Game(user=user,
                    #target=random.choice(range(1, max + 1)),
                    #attempts_allowed=attempts,
                    #attempts_remaining=attempts, 
                    canceled_game=False,
                    survived=False,
                    game_over=False, 
                    game_started=False, 
                    difficulty=setdiff)
        game.history=[]
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        #form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.canceled_game = self.canceled_game
        form.survived = self.survived
        #form.message send the good luck message.
        form.message = message
        return form

#Print items needed to craft something.
class StringMessageCraftForm(messages.Message):
    """StringMessage-- outbound showing how to craft items"""
    outmessage = messages.StringField(1, repeated=True)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    #This, I think, is the make_a move
    urlsafe_key = messages.StringField(1, required=True)
    #attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(2, required=True)
    canceled_game = messages.BooleanField(3, required = True)
    survived = messages.BooleanField(4, required = True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)

#Input form for making a new game.
class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    how_hard = messages.IntegerField(2, required=True)
    #min = messages.IntegerField(2, default=1)
    #max = messages.IntegerField(3, default=10)
    #attempts = messages.IntegerField(4, default=5)

#Response message for crafting an itme.
class CraftForm(messages.Message):
    """Used to craft an item response message"""
    user_name = messages.StringField(1, required=True)
    items_needed= messages.StringField(2, required=True)
    items_required=messages.StringField(3, required=True)
    response=messages.StringField(4, required=True)

#Input form for crafting an item.
class CraftItem(messages.Message):
    """Used to input crafting request"""
    user_name = messages.StringField(1, required=True)
    itemcraft = messages.StringField(2, required=True)

class GetUserGame(messages.Message):
    """Used to input crafting request"""
    user_name = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    total_played = messages.IntegerField(4, required=True)
    win_percentage = messages.FloatField(5, required=True)

class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)

class GetScore(messages.Message):
    """Used to set number of scores queried"""
    HowMany = messages.IntegerField(1, required=True)

class ScoreForm(messages.Message):
    """Return message form for scores"""
    name = messages.StringField(1, required=True)
    #email = messages.StringField(2)
    #wins = messages.IntegerField(3, required=True)
    #total_played = messages.IntegerField(4, required=True)
    score = messages.IntegerField(5, required=True)

class ScoreForms(messages.Message):
    items = messages.MessageField(ScoreForm, 1, repeated=True)
