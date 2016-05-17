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

    def add_win(self):
        """Add a win"""
        self.wins += 1
        self.total_played += 1
        self.put()

    def add_loss(self):
        """Add a loss"""
        self.total_played += 1
        self.put()


class Game(ndb.Model):
    """Game object"""
    word_a = ndb.PickleProperty(required=True) # secret word for user b
    word_b = ndb.PickleProperty(required=True) # secret word for user a
    word_a_guess = ndb.PickleProperty() # Convert word_a to an empty list
    word_b_guess = ndb.PickleProperty() # Convert word_b to an empty list
    attempts_remaining_a = ndb.IntegerProperty()
    attempts_remaining_b = ndb.IntegerProperty()
    user_a = ndb.KeyProperty(required=True, kind='User')
    user_b = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()
    history = ndb.PickleProperty(required=True)

    @classmethod
    def new_game(cls, user_a, user_b, word_a, word_b):
        """Creates and returns a new game"""
        game = Game(user_a=user_a,
                    user_b=user_b,
                    word_a=word_a,
                    word_b=word_b,
                    word_a_guess=[],
                    word_b_guess=[],
                    attempts_remaining_a=int(7),
                    attempts_remaining_b=int(7),
                    history=[])
        game.word_a = list(word_a)
        game.word_b = list(word_b)
        game.word_a_guess = ['_']*len(game.word_a)
        game.word_b_guess = ['_']*len(game.word_b)
        game.history = []
        game.put()
        return game

    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = GameForm(urlsafe_key=self.key.urlsafe(),
                        word_a = str(self.word_a),
                        word_b = str(self.word_b),
                        user_a=self.user_a.get().name,
                        user_b=self.user_b.get().name,
                        word_a_guess=str(self.word_a_guess),
                        word_b_guess=str(self.word_b_guess),
                        attempts_remaining_a=int(self.attempts_remaining_a),
                        attempts_remaining_b=int(self.attempts_remaining_b),
                        history=str(self.history),
                        game_over=self.game_over
                        )
#        if self.winner :
#            form.winner = self.winner.get().name
        return form

    def end_game(self, winner):
        """Ends the game"""
        self.winner = winner
        self.game_over = True
        self.put()
        loser = self.user_b if winner == self.user_a else self.user_a
        # Add the game to the score 'board'
        score = Score(date=date.today(), winner=winner, loser=loser)
        score.put()

        # Update the user models
        winner.get().add_win()
        loser.get().add_loss()


class Score(ndb.Model):
    """Score object"""
    date = ndb.DateProperty(required=True)
    winner = ndb.KeyProperty(required=True)
    loser = ndb.KeyProperty(required=True)

    def to_form(self):
        return ScoreForm(date=str(self.date),
                         winner=self.winner.get().name,
                         loser=self.loser.get().name)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    word_a = messages.StringField(2, required=True)
    word_b = messages.StringField(3, required=True)
    word_a_guess = messages.StringField(4)
    word_b_guess = messages.StringField(5)
    attempts_remaining_a = messages.IntegerField(6)
    attempts_remaining_b = messages.IntegerField(7)
    user_a = messages.StringField(8, required=True)
    user_b = messages.StringField(9, required=True)
    game_over = messages.BooleanField(10, required=True)
    winner = messages.BooleanField(11)
    history = messages.StringField(12)


class GameForms(messages.Message):
    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_a = messages.StringField(1, required=True)
    user_b = messages.StringField(2, required=True)
    word_a = messages.StringField(3, required=True)
    word_b = messages.StringField(4, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    guess = messages.StringField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    date = messages.StringField(1, required=True)
    winner = messages.StringField(2, required=True)
    loser = messages.StringField(3, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


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
