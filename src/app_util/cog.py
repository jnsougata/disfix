import asyncio
import discord
from functools import wraps
from .errors import NonCoroutine
from .origin import ApplicationCommandOrigin
from .input_chat import SubCommand, Option, SlashCommand
from .input_user import UserCommand
from .input_msg import MessageCommand
from .utils import ApplicationCommandType
from typing import Optional, ClassVar, Callable, List, Union, Dict, Any


class Cog(metaclass=type):

    __uuid__ = None
    __autocomplete__ = {}
    __mapped_checks__: dict = {}
    __temp_listeners__: dict = {}
    __mapped_container__: dict = {}
    __method_container__: dict = {}
    __sub_method_container__: dict = {}
    __command_container__: dict = {}
    __permission_container__: dict = {}
    __after_invoke_container__: dict = {}
    __before_invoke_container__: dict = {}

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
        subcommands = cls.__sub_method_container__.copy()
        setattr(cls, '__subcommands__', subcommands)
        cls.__sub_method_container__.clear()
        setattr(cls, '__self__', self)
        return self

    @classmethod
    def command(
            cls,
            *,
            name: str,
            description: str,
            dm_access: bool = True,
            category: ApplicationCommandType,
            options: Optional[List[Option]] = None,
            guild_id: int = None
    ):
        """
        Decorator for registering an application command
        inside any cog class subclassed from app_util.Cog
        """
        if options and category is ApplicationCommandType.USER or category is ApplicationCommandType.MESSAGE:
            raise ValueError("Options are only allowed for slash commands")

        if description and category is ApplicationCommandType.USER or category is ApplicationCommandType.MESSAGE:
            raise ValueError("Description is only allowed for slash commands")

        if category is ApplicationCommandType.SLASH:
            command = SlashCommand(name, description, options=options, dm_access=dm_access)
        elif category is ApplicationCommandType.USER:
            command = UserCommand(name, dm_access=dm_access)
        elif category is ApplicationCommandType.MESSAGE:
            command = MessageCommand(name, dm_access=dm_access)
        else:
            raise ValueError("Invalid command type")

        if guild_id:
            cls.__uuid__ = f"{command.uuid}_{guild_id}"
        else:
            cls.__uuid__ = command.uuid

        cls.__command_container__[cls.__uuid__] = (command, guild_id)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__method_container__[cls.__uuid__] = wrapper()
            return cls
        return decorator

    @classmethod
    def subcommand(cls, *, name: str, description: str, options: [Option] = None):
        subcommand = SubCommand(name, description, options=options)
        mapping_name = f"{cls.__uuid__}_SUBCOMMAND_{subcommand.name}"

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__sub_method_container__[mapping_name] = mapping_name, wrapper(), subcommand
            return cls
        return decorator

    @classmethod
    def default_permission(cls, permission: discord.Permissions):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__permission_container__[cls.__uuid__] = permission
                return func
            return wrapper()
        return decorator

    @classmethod
    def auto_complete(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__autocomplete__[cls.__uuid__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def check(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__mapped_checks__[cls.__uuid__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def before_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__before_invoke_container__[cls.__uuid__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def after_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__after_invoke_container__[cls.__uuid__] = coro
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
