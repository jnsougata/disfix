import asyncio
import discord
from functools import wraps
from .errors import NonCoroutine
from .app import ApplicationCommandOrigin
from typing import Optional, ClassVar, Callable, List, Union, Dict, Any


class Cog(metaclass=type):

    __identifier__ = None
    __autocomplete__ = {}
    __mapped_checks__: dict = {}
    __mapped_container__: dict = {}
    __method_container__: dict = {}
    __command_container__: dict = {}
    __temp_listeners__: dict = {}
    __permission_container__: dict = {}
    __before_invoke_container__: dict = {}
    __after_invoke_container__: dict = {}

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
        listeners = cls.__temp_listeners__.copy()
        setattr(cls, '__listeners__', listeners)
        cls.__temp_listeners__.clear()
        perms = cls.__permission_container__.copy()
        setattr(cls, '__permissions__', perms)
        cls.__permission_container__.clear()
        before_invoke = cls.__before_invoke_container__.copy()
        setattr(cls, '__before_invoke__', before_invoke)
        cls.__before_invoke_container__.clear()
        after_invoke = cls.__after_invoke_container__.copy()
        setattr(cls, '__after_invoke__', after_invoke)
        cls.__after_invoke_container__.clear()
        setattr(cls, '__self__', self)
        return self

    @classmethod
    def command(cls, command: ApplicationCommandOrigin, *, guild_id: int = None):
        """
        Decorator for registering an application command
        inside any cog class subclassed from app_util.Cog
        """
        if guild_id:
            cls.__identifier__ = f"{command._qual}_{guild_id}"
        else:
            cls.__identifier__ = command._qual

        cls.__command_container__[cls.__identifier__] = (command, guild_id)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__method_container__[cls.__identifier__] = wrapper()
        return decorator

    @classmethod
    def default_permission(cls, permission: discord.Permissions):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__permission_container__[cls.__identifier__] = permission
                return func
            return wrapper()
        return decorator

    @classmethod
    def auto_complete(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__autocomplete__[cls.__identifier__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def check(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__mapped_checks__[cls.__identifier__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def before_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__before_invoke_container__[cls.__identifier__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def after_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__after_invoke_container__[cls.__identifier__] = coro
                return func
            return wrapper()

        return decorator

    @classmethod
    def listener(cls, coro: Callable):
        """
        Decorator for adding a listener to the cog
        This listener will be called when an error occurs
        """
        if coro.__name__ == 'on_app_command':
            cls.__temp_listeners__['on_app_command'] = coro

        if coro.__name__ == 'on_app_command_error':
            cls.__temp_listeners__['on_app_command_error'] = coro

        if coro.__name__ == 'on_app_command_completion':
            cls.__temp_listeners__['on_app_command_completion'] = coro

        return coro
