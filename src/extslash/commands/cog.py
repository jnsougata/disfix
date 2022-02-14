import sys
import traceback
import asyncio
from typing import Optional, ClassVar, Callable
from abc import ABC
from functools import wraps
from .errors import NonCoroutine
from ..builder import SlashCommand
from .context import ApplicationContext


class SlashCog(ABC):

    __cog_commands__ = []
    __cog_functions__ = {}
    __cog_listener__ = None


    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        return self


    @classmethod
    def command(cls, command: SlashCommand, guild_id: int = None):
        """
        Decorator for registering a slash command
        """
        cls.__cog_commands__.append((command, guild_id))

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func

            cls.__cog_functions__[command.name] = wrapper()
        return decorator

    @classmethod
    def listener(cls, function: Callable):
        """
        Decorator for registering an error listener
        """
        cls.__cog_listener__ = function
