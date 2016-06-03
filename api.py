import logging
import endpoints
import re
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, GameForms, UserForm, UserForms
from utils import get_by_urlsafe, check_winner, replaceCharacterAtIndexInString

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='hangman', version='v1')
class HangmanAPI(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username and an email"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        if not request.user_name or request.email==None:
            raise endpoints.BadRequestException('You must provide a username and email')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all Users ranked by their win percentage"""
        users = User.query(User.total_played > 0).fetch()
        users = sorted(users, key=lambda x: x.win_percentage, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user_a = User.query(User.name == request.user_a).get()
        user_b = User.query(User.name == request.user_b).get()
        if  user_a == None or user_b == None:
            raise endpoints.NotFoundException(
                    'One of users with that name does not exist!')
        else :
            word_a = request.word_a
            word_b = request.word_b
            game = Game.new_game(user_a.key, user_b.key, word_a, word_b)

            return game.to_form()

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form()
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(ndb.OR(Game.user_a == user.key,
                                  Game.user_b == user.key)).\
            filter(Game.game_over == False)
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(response_message=GameForms,
                      path='all_games',
                      name='get_all_games',
                      http_method='GET')
    def get_all_games(self, request):
        """Return all games"""
        return GameForms(items=[game.to_form() for game in Game.query()])

    @endpoints.method(response_message=GameForms,
                      path='all_active_games',
                      name='get_all_active_games',
                      http_method='GET')
    def get_all_active_games(self, request):
        """Return all active games"""
        games = Game.query(Game.game_over!=True)
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Delete a game. Game must not have ended to be deleted"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.key.delete()
            return StringMessage(message='Game with key: {} deleted.'.
                                 format(request.urlsafe_game_key))
        elif game and game.game_over:
            raise endpoints.BadRequestException('Game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        if game.game_over:
            raise endpoints.NotFoundException('Game already over')

        # Get user name
        user = User.query(User.name == request.user_name).get()
        # Check user is valid
        if user == None :
            raise endpoints.NotFoundException('User not found!')
        # Signifiers for which user is guessing
        a = True if (user.key == game.user_a) else False
        word_x = game.word_a if a == True else game.word_b
        word_x_guess = game.word_a_guess if a == True else game.word_b_guess
        guess = request.guess

        # Verify user has moves left
        if a == True :
            if game.attempts_remaining_a == 0:
                raise endpoints.BadRequestException('You have been hanged!')
        else:
            if game.attempts_remaining_b == 0:
                raise endpoints.BadRequestException('You have been hanged!')

        # Verify move is valid
        x = re.compile('[a-zA-Z]')
        if not x.match(guess):
            raise endpoints.BadRequestException('Invalid charachter!')

        if len(list(guess)) > 1:
            raise endpoints.BadRequestException('You can only enter 1 character!')

        # Verify in history that guess has not been guessed before
        if a == True :
            for (u , s) in game.history:
                if u == 'A' and s == guess:
                        raise endpoints.BadRequestException('You already guessed that letter!')
        else :
            for (u , s) in game.history:
                if u == 'B' and s == guess:
                        raise endpoints.BadRequestException('You already guessed that letter!')

        # Get guess and place it in word_x_guess if correct
        for num in range(0, len(word_x)):
            if guess in str(word_x[num]):
                word_x_guess = replaceCharacterAtIndexInString(word_x_guess,num,guess)

        # If incorrect down one counter on attempts_remaining
        if guess not in str(word_x):
            if a == True :
                game.attempts_remaining_a -= 1
            else:
                game.attempts_remaining_b -= 1

        if game.attempts_remaining_a == 0 and game.attempts_remaining_b ==0 :
            game.key.delete()
            raise endpoints.NotFoundException('Both have been hanged, losers!')
        # Append a move to the history
        game.history.append(('A' if a else 'B', guess))

        #Check winner
        winner = check_winner(word_x, word_x_guess)

        if winner:
           game.end_game(user.key)
           game.to_form()
           return StringMessage(message='You have won!')
        game.put()
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form()



    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(ndb.OR(Score.winner == user.key,
                                    Score.loser == user.key))
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining_a + \
                                        game.attempts_remaining_b
                                        for game in games])
            average = float(total_attempts_remaining)/count/2
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))

api = endpoints.api_server([HangmanAPI])
