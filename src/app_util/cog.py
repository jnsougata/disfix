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

    __qual__ = None
    __mapped_jobs__: dict = {}
    __mapped_container__: dict = {}
    __method_container__: dict = {}
    __command_container__: dict = {}
    __error_listener__: Any = None


    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        commands = cls.__command_container__.copy()
        setattr(cls, '__commands__', commands)
        cls.__command_container__.clear()
        methods = cls.__method_container__.copy()
        setattr(cls, '__methods__', methods)
        cls.__method_container__.clear()
        jobs = cls.__mapped_jobs__.copy()
        setattr(cls, '__jobs__', jobs)
        cls.__mapped_jobs__.clear()
        listener = cls.__error_listener__
        setattr(cls, '__listener__', listener)
        setattr(cls, '__this__', self)
        return self


    @classmethod
    def command(cls, command: BaseApplicationCommand, guild_id: int = None):
        """
        Decorator for registering an application command
        """
        if guild_id:
            qualified_name = f"{command._qual}_{guild_id}"
        else:
            qualified_name = command._qual
        cls.__qual__ = qualified_name
        cls.__command_container__[qualified_name] = (command, guild_id)

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
                cls.__mapped_jobs__[cls.__qual__] = job
                return func
            return wrapper()

        return decorator


    @classmethod
    def listener(cls, func: Callable):
        """
        Decorator for registering an error listener
        """
        cls.__error_listener__ = func
        return func
