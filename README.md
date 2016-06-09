#FSND Project 4 GameAPI (Hangman)

Only accepts english unicode letters for now :)

## [Overview](#Overview)

## [Models](#Models)
*  [NDB User](#user)
*  [NDB Game](#game)
*  [NDB Score](#score)

## [Forms](#Forms)
*  [Msg GameForm](#GameForm)
*  [Msg GameForms](#GameForms)
*  [Msg NewGameForm](#NewGameForm)
*  [Msg MakeMoveForm](#MakeMoveForm)
*  [Msg ScoreForm](#ScoreForm)
*  [Msg ScoreForms](#ScoreForms)
*  [Msg UserForm](#UserForm)
*  [Msg UserForms](#UserForms)

## [Endpoints](#Endpoints)
*   [@ create_user](#create_user)
*   [@ get_user_rankings](#get_user_rankings)
*   [@ new_game](#new_game)
*   [@ get_game](#get_game)
*   [@ get_user_games](#get_user_games)
*   [@ get_all_games](#get_all_games)
*   [@ get_all_active_games](#get_all_active_games)
*   [@ cancel_game](#cancel_game)
*   [@ make_move](#make_move)
*   [@ get_game_history](#get_game_history)
*   [@ get_scores](#get_scores)
*   [@ get_user_scores](#get_user_scores)
*   [@ get_average_attempts](#get_average_attempts)

## [Using the api](#Using-the-api)

## Overview

This is a simple hangman game API for udacity's FSND Make a Game Project.
Uses the Google App Engine platform and the NDB libraries. The game logic goes
as follows (once you have diferent users and a game is created):
- user_x will try to guess word_x .
- guesses will be done only letter by letter.
- turns will not apply.
- if a user runs out of attempts he will be hanged and will await to see if .
  his/her opponent has better luck.
- if both users fail to guess their words the game will be deleted.
When games get to full completion scores are recorded and a leaderboard based
on wins can be generated.

## Models

### user
User model for profile consisting of :
* name - StringProperty
* email - StringProperty
* wins - IntegerProperty
* total_played - IntegerProperty

It also has four properties for :
* win_percentage
Get total played and make a percentage against the wins.

* to_form
Present the model as [UserForm](#UserForm).

* add_win
Add a counter to total_played and a win to wins.

* add_loss
Only add a counter to total_played.

### game
Game model for game objects:
* word_a          - PickleProperty
* word_b          - PickleProperty
* word_a_guess    - PickleProperty
* word_b_guess    - PickleProperty
* attempts_remaining_a - IntegerProperty
* attempts_remaining_b - IntegerProperty
* user_a          - KeyProperty
* user_b          - KeyProperty
* game_over       - BooleanProperty
* winner          - KeyProperty
* history         - PickleProperty
* message         - StringProperty

It has three classmethods:
* new_game
Get user_a/user_b and word_a/word_b to create a new game.
* to_form
Returns a [GameForm](#GameForm) representation of the Game.
* end_game
End the game and add result to score

### score
Score model for finished games:
* date            - DateProperty
* winner          - KeyProperty
* loser           - KeyProperty

Has a to_form function for return a ScoreForm representation of score.

## Forms

### GameForm
GameForm for outbound game state information:
* urlsafe_key     - StringField
* word_a          - StringField
* word_b          - StringField
* word_a_guess    - StringField
* word_b_guess    - StringField
* attempts_remaining_a - IntegerField
* attempts_remaining_b - IntegerField
* user_a          - StringField
* user_b          - StringField
* game_over       - BooleanField
* winner          - StringField
* history         - StringField
* message         - StringField

### GameForms
Container for multiple GameForm objects.

### NewGameForm
Used to create a new game:
* user_a          - StringField
* user_b          - StringField
* word_a          - StringField
* word_b          - StringField

### MakeMoveForm
Used to make a move in an existing game:
* user_name       - StringField
* guess           - StringField

### ScoreForm
ScoreForm for outbound Score information:
* date            - StringField
* winner          - StringField
* loser           - StringField

### ScoreForms
Return multiple ScoreForm objects.

### UserForm
UserForm for outbound User information:
* name            - StringField
* email           - StringField
* wins            - IntegerField
* total_played    - IntegerField
* win_percentage  - FloatField

### UserForms
Return multiple UserForm objects.

## Endpoints

### create_user
- Path: 'user'
- Method: POST
- Parameters: user_name, email
- Returns: Message confirming creation of the User.
- Description: Makes a new user entry in User model. Requires a new name not
  found in the database and an email.

### get_user_rankings
- Path: 'user/ranking'
- Method: GET
- Parameters: None
- Returns: UserForms orderered by win_percentage.
- Description: Return all Users ranked by their win percentage.

### new_game
- Path: 'game'
- Method: POST
- Parameters: user_a, user_b, word_a, word_b
- Returns: GameForm with game data.
- Description: Create a new game. Requires two usernames and two different guess
  words.

### get_game
- Path: 'game/{urlsafe_game_key}'
- Method: GET
- Parameters: urlsafe_game_key
- Returns: GameForm with game data or 404 exception.
- Description: Given a valid urlsafe_game_key return the game data.

### get_user_games
- Path: 'user/games'
- Method: GET
- Parameters: user_name
- Returns: GameForms with game data or 400 exception (user not found).
- Description: Given a user, return active games for that user.

### get_all_games
- Path: 'all_games'
- Method: GET
- Parameters: None
- Returns: GameForms with game data.
- Description: Returns all games being played and ever played.

### get_all_active_games
- Path: 'all_active_games'
- Method: GET
- Parameters: None
- Returns: GameForms with game data.
- Description: Returns only all active games.

### cancel_game
- Path: 'game/{urlsafe_game_key}'
- Method: DELETE
- Parameters: urlsafe_game_key
- Returns: Message confirming deletion of game or exceptions 400(game over)
  / 404(game not found).
- Description: Given a urlsafe_game_key, deletes the game if the game is
  not over and game is found.

### make_move
- Path: 'game/{urlsafe_game_key}'
- Method: GET
- Parameters: urlsafe_game_key, user_name, guess
- Returns: GameForm with game data, 404 exception (User or game not found, or
  both have lost) or 400 exception (invalid or repeated character).
- Description: First it checks the game exists and is not over. Then gets the
  user and sets signifiers for his values in the game, for later checking the
  guess (only a single english unicode character) against his secret word and
  returning if the guess was correct, if the game has been won or if his
  attempts_remaining have reached 0. Every time this endpoint is used it
  updates the memcached average attemps remaining.

### get_game_history
- Path: 'game/{urlsafe_game_key}'
- Method: GET
- Parameters: urlsafe_game_key
- Returns: GameForm with game data or 404 exception.
- Description: Given a urlsafe_game_key check its existance, if it exixts
  return its history.

### get_scores
- Path: 'scores'
- Method: GET
- Parameters: None
- Returns: ScoreForms with user scores data.
- Description: Return all scores of games ever played.

### get_user_scores
- Path: 'scores/user/{user_name}'
- Method: GET
- Parameters: user_name
- Returns: ScoreForms with given user's scores data or 404 exception(User
  Not Found).
- Description: Return all scores of games ever played by the given user.

### get_average_attempts
- Path: 'games/average_attempts'
- Method: GET
- Parameters: None
- Returns: StringMessage with memcached average moves remaining.
- Description: Get an average of attempts remaining across all games.

## Using-the-api
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application


Daniel Carrillo Harris 2016 (carrharr) danielcarrilloharris@gmail.com
