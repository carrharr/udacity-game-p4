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
from utils import get_by_urlsafe, check_winner, check_full, replaceCharacterAtIndexInString

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
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
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
        if not user_a and user_b:
            raise endpoints.NotFoundException(
                    'One of users with that name does not exist!')
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
        # Signifiers for which user is guessing
        a = True if (user.key == game.user_a) else False
        word_x = game.word_a if a == True else game.word_b
        word_x_guess = game.word_a_guess if a == True else game.word_b_guess
        attempts_remaining_x = game.attempts_remaining_a if a == True else \
                                game.attempts_remaining_b
        guess = request.guess
        # Verify move is valid
        #if guess != re.match([a-zA-Z]):
        #    raise endpoints.BadRequestException('Invalid charachter!')

        if len(list(guess)) > 1:
            raise endpoints.BadRequestException('You can only enter 1 \
                                                character!')

        # This is probably badly written
        # Need testing
        #if word_x_guess[guess] != '_':
        #    raise endpoints.BadRequestException('You have already guessed that \
        #                                        letter!')
        """
        This next thing is not working properly.
        """

        for num in range(0, len(word_x)):
            if guess == word_x[num]:
                word_x_guess = replaceCharacterAtIndexInString(word_x_guess,\
                                                                num,guess)
            else:
                attempts_remaining_x = (attempts_remaining_x) - 1

            # Check guess against word_a
            # If correct change underscores for letters in word_a_guess
            # If word is complete do winner
            # If not add -1 counter on attempts_remaining_x
            # If attempts_remaining_x == 0 , do loser
        # Append a move to the history
        game.history.append(('A' if a else 'B', guess))

        """
        Have to redo the winner var to get winner when word_x and word_x_guess
        match.

        This next_move and tie is rubbish, will only keep the <if winner> and
        else it to restart function as it is two users playing independently
        """

#        winner = check_winner(word_x)

#        if winner:
#           game.end_game(user.key)
#        else:
#            # Send reminder email
#            taskqueue.add(url='/tasks/send_move_email',
#                          params={'user_key': game.next_move.urlsafe(),
#3                                  'game_key': game.key.urlsafe()})
        game.put()
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
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([HangmanAPI])