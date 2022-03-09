import asyncio
from functools import wraps
from .errors import NonCoroutine
from .app import ApplicationCommandOrigin
from typing import Optional, ClassVar, Callable, List, Union, Dict, Any



class Cog(metaclass=type):

    __qual__ = None
    __autocomplete__ = {}
    __mapped_checks__: dict = {}
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
        checks = cls.__mapped_checks__.copy()
        setattr(cls, '__checks__', checks)
        cls.__mapped_checks__.clear()
        automatics = cls.__autocomplete__.copy()
        setattr(cls, '__automatics__', automatics)
        listener = cls.__error_listener__
        setattr(cls, '__listener__', listener)
        setattr(cls, '__this__', self)
        return self


    @classmethod
    def command(cls, command: ApplicationCommandOrigin, *, guild_id: int = None):
        """
        Decorator for registering an application command
        inside any cog class subclassed from app_util.Cog
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
    def before_invoke(cls, *, check: Callable = None, autocomplete_handler: Callable = None):
        """
        Decorator for adding a checks and sending respond if the check fails
        Also adds an autocomplete function if provided. The autocomplete function
        will be called when the user starts typing an option an application command
        with autocomplete enabled.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if check:
                    cls.__mapped_checks__[cls.__qual__] = check
                if autocomplete_handler:
                    cls.__autocomplete__[cls.__qual__] = autocomplete_handler
                return func
            return wrapper()

        return decorator


    @classmethod
    def listener(cls, coro: Callable):
        """
        Decorator for adding a listener to the cog
        This listener will be called when an error occurs
        """
        cls.__error_listener__ = coro
        return coro
