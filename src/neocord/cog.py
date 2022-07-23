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


class Temp:
    ROOT = None
    GROUP = None
    SUBCOMMAND = None
    GRP_SUBCOMMAND = None


T = Temp()


class Cog(metaclass=type):
    _container: ClassVar[Dict[str, Any]] = {}
    _listeners: ClassVar[Dict[str, Any]] = {}

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.__setattr__("cls", self)
        self.__setattr__("__container__", cls._container.copy())
        self.__setattr__("__listeners__", cls._listeners.copy())
        cls._listeners.clear()
        cls._container.clear()
        return self

    @classmethod
    def command(
            cls,
            name: str, description: str = None,
            *,
            dm_access: bool = True, category: CommandType = CommandType.SLASH, guild_id: int = None
    ):
        if description and category is not CommandType.SLASH:
            raise ValueError("Description is only allowed for slash commands")

        if category is CommandType.SLASH:
            command = SlashCommand(name, description, dm_access=dm_access)
        elif category is CommandType.USER:
            command = UserCommand(name, dm_access=dm_access)
        elif category is CommandType.MESSAGE:
            command = MessageCommand(name, dm_access=dm_access)
        else:
            raise ValueError("Invalid command type")

        T.ROOT = command._custom_id
        T.GROUP = None
        T.SUBCOMMAND = None
        T.GRP_SUBCOMMAND = None

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls._container[command._custom_id] = {
                "command": {
                    "object": command,
                    "method": wrapper(),
                    "check": None,
                    "autocompletes": None,
                    "before_invoke": None,
                    "after_invoke": None,
                    "guild_id": guild_id,
                },
                "subcommands": {},
                "groups": {},
            }
            return cls
        return decorator

    @classmethod
    def option(cls, option: Option):
        if T.SUBCOMMAND:
            cls._container[T.ROOT]["subcommands"][T.SUBCOMMAND]["object"]._inject_option(option)
        elif T.GROUP:
            cls._container[T.ROOT]["groups"][T.GROUP]["subcommands"][T.GRP_SUBCOMMAND]["object"]._inject_option(option)
        else:
            cls._container[T.ROOT]["command"]["object"]._inject_option(option)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            return wrapper()
        return decorator

    @classmethod
    def subcommand(cls, name: str, description: str):
        if T.GROUP:
            T.SUBCOMMAND = None
            T.GRP_SUBCOMMAND = name
            subcommand = SubCommand(name, description)
            cls._container[T.ROOT]["groups"][T.GROUP]["subcommands"][name] = {"object": subcommand, "method": None}
            ref = cls._container[T.ROOT]["groups"][T.GROUP]["subcommands"][name]

        elif T.SUBCOMMAND:
            T.GROUP = None
            T.SUBCOMMAND = name
            cls._container[T.ROOT]["subcommands"][name] = {"object": SubCommand(name, description), "method": None}
            ref = cls._container[T.ROOT]["subcommands"][name]

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            ref["method"] = wrapper()
            return cls
        return decorator

    @classmethod
    def group(cls, name: str, description: str):
        T.GROUP = name
        T.GRP_SUBCOMMAND = None
        cls._container[T.ROOT]["groups"][name] = {
            "object": SubCommandGroup(name, description),
            "subcommands": {},
            "method": None,
        }

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls._container[T.ROOT]["groups"][name]["method"] = wrapper()
            return cls
        return decorator

    @classmethod
    def default_permission(cls, permission: discord.Permissions):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[T.ROOT]["command"]["object"]._inject_permission(permission)
                return cls
            return wrapper()
        return decorator

    @classmethod
    def auto_complete(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[T.ROOT]["command"]["autocompletes"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def check(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[T.ROOT]["command"]["check"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def before_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[T.ROOT]["command"]["before_invoke"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def after_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[T.ROOT]["command"]["after_invoke"] = coro
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
            cls._listeners[coro.__name__] = coro
            return cls


cog = Cog
