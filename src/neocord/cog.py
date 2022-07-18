import asyncio
import discord
from functools import wraps
from .utils import CommandType
from .errors import NonCoroutine
from .input_user import UserCommand
from .input_msg import MessageCommand
from .origin import ApplicationCommandOrigin
from typing import Optional, ClassVar, Callable, List, Union, Dict, Any
from .input_chat import SubCommand, Option, SlashCommand, SubCommandGroup


class Cog(metaclass=type):

    __uid__ = None
    __autocomplete__ = {}
    __mapped_checks__: dict = {}
    __temp_listeners__: dict = {}
    __mapped_container__: dict = {}
    __method_container__: dict = {}
    __sub_method_container__: dict = {}
    __sub_group_method_container__: dict = {}
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
            description: str = None,
            dm_access: bool = True,
            category: CommandType,
            options: Optional[List[Option]] = None,
            guild_id: int = None
    ):
        """
        Decorator for registering an application command
        inside any cog class subclassed from neocord.Cog
        """
        if options and category is not CommandType.SLASH:
            raise ValueError("Options are only allowed for slash commands")

        if description and category is not CommandType.SLASH:
            raise ValueError("Description is only allowed for slash commands")

        if category is CommandType.SLASH:
            command = SlashCommand(name, description, options=options, dm_access=dm_access)
        elif category is CommandType.USER:
            command = UserCommand(name, dm_access=dm_access)
        elif category is CommandType.MESSAGE:
            command = MessageCommand(name, dm_access=dm_access)
        else:
            raise ValueError("Invalid command type")

        cls.__uid__ = command._custom_id
        cls.__command_container__[cls.__uid__] = command, guild_id

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__method_container__[cls.__uid__] = wrapper()
            return cls
        return decorator

    @classmethod
    def subcommand(cls, *, name: str, description: str, options: [Option] = None):
        subcommand = SubCommand(name, description, options=options)
        mapping_name = f"{cls.__uid__}*{subcommand.name}"

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__sub_method_container__[mapping_name] = mapping_name, wrapper(), subcommand
            return cls
        return decorator

    @classmethod
    def subcommand_group(cls, *, name: str, description: str, subcommands: [SubCommand] = None):
        subcommand_group = SubCommandGroup(name, description, subcommands=subcommands)
        mapping_name = f"{cls.__uid__}_SUBCOMMAND_GROUP_{subcommand_group.name}"

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__sub_group_method_container__[mapping_name] = mapping_name, wrapper(), subcommand_group
            return cls
        return decorator

    @classmethod
    def default_permission(cls, permission: discord.Permissions):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__permission_container__[cls.__uid__] = permission
                return func
            return wrapper()
        return decorator

    @classmethod
    def auto_complete(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__autocomplete__[cls.__uid__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def check(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__mapped_checks__[cls.__uid__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def before_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__before_invoke_container__[cls.__uid__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def after_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__after_invoke_container__[cls.__uid__] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def listener(cls, coro: Callable):
        """
        Decorator for adding a listener to the cog
        This listener will be called when an error occurs
        """
        allowed_methods = [
            'on_app_command',
            'on_app_command_error',
            'on_app_command_completion',
        ]
        if coro.__name__ not in allowed_methods:
            raise ValueError(f"Invalid method name. Allowed methods are: {' | '.join(allowed_methods)}")
        else:
            cls.__temp_listeners__[coro.__name__] = coro
            return cls


cog = Cog
