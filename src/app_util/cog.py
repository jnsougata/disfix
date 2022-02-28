import inspect
import asyncio
import traceback
from abc import ABC, ABCMeta
from functools import wraps
from .errors import NonCoroutine
from .app import BaseApplicationCommand
from .context import Context
from typing import Optional, ClassVar, Callable, List, Union, Dict, Any



class Cog(metaclass=type):

    __error_listener__: dict = {}
    __method_container__: dict = {}
    __object_container__: dict = {}
    __mapped_container__: dict = {}
    __mapped_jobs__: dict = {}

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
    def command(cls, command: BaseApplicationCommand, guild_id: int = None):
        """
        Decorator for registering a slash command
        """
        if guild_id:
            qualified_name = f"{command._qual}_{guild_id}"
        else:
            qualified_name = command._qual

        cls.__object_container__[qualified_name] = (command, guild_id)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__method_container__[qualified_name] = wrapper()
        return decorator

    @classmethod
    def before_invoke(cls, job: Callable):
        """
        Decorator for adding a pre-command job w.r.t checks
        :job: The function containing the job to be executed
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__mapped_jobs__[func.__name__] = job
                return func

            return wrapper()

        return decorator


    @classmethod
    def listener(cls, func: Callable):
        """
        Decorator for registering an error listener
        """
        cls.__error_listener__ = {'callable': func, 'parent': None}
        return func
