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
    __container: ClassVar[Dict[str, Any]] = {}
    __listeners: ClassVar[Dict[str, Any]] = {}

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        cls.__container[self.__uid__]["origin"] = self
        self.__setattr__("__container__", cls.__container.copy())
        self.__setattr__("__listeners__", cls.__listeners.copy())
        cls.__listeners.clear()
        cls.__container.clear()
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

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__container[command._custom_id] = {
                "command": {
                    "object": command,
                    "method": wrapper(),
                    "check": None,
                    "autocompletes": None,
                    "permissions": None,
                    "before_invoke": None,
                    "after_invoke": None,
                    "guild_id": guild_id,
                },
                "subcommands": {},
                "groupcommands": {},
                "origin": None,
            }
            return cls
        return decorator

    @classmethod
    def subcommand(cls, *, name: str, description: str, options: [Option] = None):
        subcommand = SubCommand(name, description, options=options)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__container[cls.__uid__]["subcommands"][subcommand.name] = {
                "method": wrapper(),
                "object": subcommand
            }
            return cls
        return decorator

    @classmethod
    def group_command(cls, *, name: str, description: str, subcommands: [SubCommand] = None):
        group = SubCommandGroup(name, description, subcommands=subcommands)
        mname = f"{cls.__uid__}**{group.name}"

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls.__container[cls.__uid__]["groupcommands"][group.name] = {
                "object": group,
                "method": wrapper(),
                "subcommands": {}
            }
            return cls
        return decorator

    @classmethod
    def default_permission(cls, permission: discord.Permissions):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__container[cls.__uid__]["command"]["permissions"] = permission
                return func
            return wrapper()
        return decorator

    @classmethod
    def auto_complete(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__container[cls.__uid__]["command"]["autocompletes"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def check(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__container[cls.__uid__]["command"]["check"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def before_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__container[cls.__uid__]["command"]["before_invoke"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def after_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.__container[cls.__uid__]["command"]["after_invoke"] = coro
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
            cls.__listeners[coro.__name__] = coro
            return cls


cog = Cog
