import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    total_played = ndb.IntegerProperty(default=0)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)   


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

class Game(ndb.Model):
    """Game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    survived = ndb.BooleanProperty(required=True, default=False)
    #history = ndb.PickleProperty(required=True)
    canceled_game = ndb.BooleanProperty(required=True, default=False)
    #target = ndb.IntegerProperty(required=True)
    #attempts_allowed = ndb.IntegerProperty(required=True)
    #attempts_remaining = ndb.IntegerProperty(required=True, default=5)
    #game_over = ndb.BooleanProperty(required=True, default=False)
    #user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        #if max < min:
            #raise ValueError('Maximum must be greater than minimum')
        game = Game(user=user,
                    #target=random.choice(range(1, max + 1)),
                    #attempts_allowed=attempts,
                    #attempts_remaining=attempts, 
                    canceled_game=False,
                    survived=False,
                    game_over=False)
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


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    #min = messages.IntegerField(2, default=1)
    #max = messages.IntegerField(3, default=10)
    #attempts = messages.IntegerField(4, default=5)
