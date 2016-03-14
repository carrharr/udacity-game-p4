#!/usr/bin/env python
"""models.py
Models for Udacity's Project 4 'Design a Game' by CarrHarr github.com/carrharr
"""
__author__ = 'danielcarrilloharris@gmail.com (Daniel Carrillo Harris)'

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

class ConflictException(endpoints.ServiceException):
    """ConflictException -- exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT

#-----------------Player Entities ----------------------------------------------
class Player(ndb.Model):
	""" Player -- Player profile object. """
    PlayerKey = ndb.StringProperty()
	nickname  = ndb.StringProperty(required=True)
	email  = nbd.StringProperty()
    level  = ndb.IntegerProperty()
    games  = ndb.StringProperty(repeated=True)
    characters = ndb.StructuredProperty(PlayerCharacters, repeated=True)

class PlayerCharacters(ndb.Model):
    """ Character -- Character Objects. """
    name = ndb.StringProperty()
    character = ndb.StringProperty()
    level = ndb.IntegerProperty()
    bodyhitprob = ndb.FloatProperty()
    longhitprob = ndb.FloatProperty()
    attack  = ndb.IntegerProperty()
    health  = ndb.IntegerProperty()
    shield  = ndb.IntegerProperty()
    items   = ndb.StructuredProperty(Item, repeated=True)
#------------------Game Entities -----------------------------------------------
class Game(ndb.Model):
    GameKey = ndb.StringProperty()
    MapKey  = ndb.StringProperty()
    Created = ndb.DateTimeProperty()
    Turn    = ndb.IntegerProperty()
    State   = ndb.BooleanProperty(default=False)

    @property
    def gameplays(self):
        return GamePlay.query(ancestor=self.key)

class GamePlay(ndb.Model):
    GamePlayKey = ndb.StringProperty()
    PlayerKey   = ndb.StringProperty()
    PlayerTurn  = ndb.StringProperty()
    PlayerPosition = ndb.StringProperty()
    PlayerAvailableMoves = ndb.IntegerProperty()
    PlayerHealth   = ndb.IntegerProperty(max_value=1000)
    PlayerShield   = ndb.IntegerProperty(max_value=)
    PlayerAttack   = ndb.IntegerProperty()
#-------------------Game Options Entities --------------------------------------

class Map(ndb.Model):
    pass

class Item(ndb.Model):
    pass
