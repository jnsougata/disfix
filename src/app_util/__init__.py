"""
Discord API Wrapper Extension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A basic slash command extension for discord.py.

:copyright: (c) 2022-present jnsougata
:license: MIT, see LICENSE for more details.

"""

__title__ = 'app_util'
__author__ = 'jnsougata'
__license__ = 'MIT'
__version__ = '0.0.3'
__copyright__ = 'Copyright 2022-present jnsougata'


from .bot import Bot
from .cog import Cog
from .errors import *
from .app import Overwrite
from .context import Context
from .slash_input import *
from .user_input import UserCommand
from .msg_input import MessageCommand
