import logging
from google.appengine.ext import ndb
import endpoints

def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def check_winner(word_x, word_x_guess):
    """Check the board. If there is a winner, return the symbol of the winner"""
    """Change from board to word_x to word_x_guess comparison """

    if word_x == word_x_guess :
        return True
    else:
        return False

def check_full(board):
    """Return true if the board is full"""
    for cell in board:
        if not cell:
            return False
    return True

def replaceCharacterAtIndexInString(s,index,newCharacter):
    """
    Returns a new string, identical to s, except that the character at the
    specified index is replaced with the specified new character.
    """
    name = s
    name[index]= newCharacter
    return name
    
