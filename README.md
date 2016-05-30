#FSND Project 4 GameAPI (Hangman)

Only accepts english unicode letters for now :)

## [Overview](#Overview)

## [Models](#Models)
*  [User](#user)
*  [Game](#game)
*  [Score](#score)

## [Forms](#Forms)
*  [GameForm](#GameForm)
*  [GameForms](#GameForms)
*  [NewGameForm](#NewGameForm)
*  [MakeMoveForm](#MakeMoveForm)
*  [ScoreForm](#ScoreForm)
*  [ScoreForms](#ScoreForms)
*  [UserForm](#UserForm)
*  [UserForms](#UserForms)

## [Endpoints](#Endpoints)
*   [create_user](#create_user)
*   [get_user_rankings](#get_user_rankings)
*   [new_game](#new_game)
*   [get_game](#get_game)
*   [get_user_games](#get_user_games)
*   [get_all_games](#get_all_games)
*   [get_all_active_games](#get_all_active_games)
*   [cancel_game](#cancel_game)
*   [make_move](#make_move)
*   [get_game_history](#get_game_history)
*   [get_scores](#get_scores)
*   [get_user_scores](#get_user_scores)
*   [get_average_attempts](#get_average_attempts)

## [Using the api](#Using-the-api)

## Overview

This is a simple hangman game API for udacity's FSND Make a Game Project.
Uses the Google App Engine platform and the NDB libraries. The idea was to
create an API that allowed a multiplayer hangman experience, in which to win,
you must guess the word before your opponent. At the moment the API consists of
the basic features needed to play the game, though social features like social
media logins and in-game friends are not implemented yet. Game creation from two
different devices at the same time has not been implemented either.(ie. Two friends
from their respective phones make a game entering only their user and their
opponents secret word).

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

### get_user_rankings

### new_game

### get_game

### get_user_games

### get_all_games

### get_all_active_games

### cancel_game

### make_move

### get_game_history

### get_scores

### get_user_scores

### get_average_attempts

## TODO

Whats left to do?

Daniel Carrillo Harris 2016 (carrharr) danielcarrilloharris@gmail.com
