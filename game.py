#!/usr/bin/env/ python
"""game.py
Game Endpoints for Udacity's Project 4 'Design a Game' by CarrHarr github.com/carrharr
"""
__author__ = 'danielcarrilloharris@gmail.com (Daniel Carrillo Harris)'

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import ConflictException
from models import Player
from models import PlayerCharacters
from models import Game
from models import gameplays
from models import GamePlay
from models import Map
from models import Item

from characterdefaults import TANK, HEALER, WIZARD


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@endpoints.api(name='UdacityGame', version='v0.1', audiences=[ANDROID_AUDIENCE],
    allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID, ANDROID_CLIENT_ID, IOS_CLIENT_ID],
    scopes=[EMAIL_SCOPE])
class GameApi(remote.Service):
    """Game API v0.1"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

api = endpoints.api_server([GameApi]) # register API
