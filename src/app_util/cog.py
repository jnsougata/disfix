import sys
import inspect
import asyncio
import traceback
from abc import ABC, ABCMeta
from functools import wraps
from .errors import NonCoroutine
from .slash_input import SlashCommand
from .user_input import UserCommand
from .msg_input import MessageCommand
from .context import Context
from typing import Optional, ClassVar, Callable, List, Union, Dict, Any



class Cog(metaclass=type):

    __error_listener__: dict = {}
    __method_container__: dict = {}
    __object_container__: dict = {}
    __mapped_container__: dict = {}

    def __new__(cls, *args, **kwargs):
        cls.__error_listener__['parent'] = cls
        elems = inspect.getfullargspec(cls).args
        elems.pop(0)
        arg_names = elems
        arg_list = list(args)
        for arg, value in zip(arg_names, arg_list):
            setattr(cls, arg, value)
        copied = cls.__object_container__.copy()
        for name, data in copied.items():
            cls.__mapped_container__[name] = {
                "parent": cls,
                "object": data[0],
                "guild_id": data[1]
            }
            cls.__object_container__.pop(name)
        return cls


    @classmethod
    def command(cls, command: [SlashCommand, UserCommand, MessageCommand], guild_id: int = None):
        """
        Decorator for registering a slash command
        """
        cls.__object_container__[command._map] = (command, guild_id)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__method_container__[command._map] = wrapper()
        return decorator

    @classmethod
    def listener(cls, func: Callable):
        """
        Decorator for registering an error listener
        """
        cls.__error_listener__ = {'callable': func, 'parent': None}
        return func
