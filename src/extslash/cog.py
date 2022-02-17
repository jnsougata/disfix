import sys
import traceback
import asyncio
from abc import ABC, ABCMeta
import inspect
from functools import wraps
from .errors import NonCoroutine
from .builder import SlashCommand
from .context import ApplicationContext
from typing import Optional, ClassVar, Callable, List, Union, Dict, Any



class Cog(metaclass=type):


    __cog_commands__: dict = {}
    __cog_functions__: dict = {}
    __cog_listener__: Callable = None
    __cog_based_commands__: dict = {}

    def __new__(cls, *args, **kwargs):
        elems = inspect.getfullargspec(cls).args
        elems.pop(0)
        arg_names = elems
        arg_list = list(args)
        for arg, value in zip(arg_names, arg_list):
            setattr(cls, arg, value)
        copied_commands = cls.__cog_commands__.copy()
        for name, data in copied_commands.items():
            cls.__cog_based_commands__[name] = {"class": cls, "command": data[0], "guild_id": data[1]}
            cls.__cog_commands__.pop(name)
        instance = super().__new__(cls)
        return instance


    @classmethod
    def command(cls, command: SlashCommand, guild_id: int = None):
        """
        Decorator for registering a slash command
        """
        cls.__cog_commands__[command.name] = (command, guild_id)

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
