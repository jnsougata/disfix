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
    _temp_id: ClassVar[str] = None
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

        cls._temp_id = command._custom_id

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
        if '*' not in cls._temp_id:
            cls._container[cls._temp_id]["command"]["object"]._inject_option(option)
        elif '**' in cls._temp_id:
            custom_id = cls._temp_id.split('**')[-1]
            temp = cls._temp_id.split('**')[0]
            sub_name = temp.split('*')[0]
            gr_name = temp.split('*')[-1]
            cls._container[custom_id]["groups"][gr_name]["subcommands"][sub_name]["object"]._inject_option(option)
        else:
            sub_name = cls._temp_id.split('*')[0]
            custom_id = cls._temp_id.split('*')[-1]
            cls._container[custom_id]["subcommands"][sub_name]["object"]._inject_option(option)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            return wrapper()
        return decorator

    @classmethod
    def subcommand(cls, name: str, description: str):
        if '**' in cls._temp_id:
            custom_id = cls._temp_id.split('**')[-1]
            group_name = cls._temp_id.split('**')[0].split('*')[-1]
            subcommand = SubCommand(name, description)
            cls._container[custom_id]["groups"][group_name]["subcommands"][name] = {
                "object": subcommand,
                "method": None,
            }
            ref = cls._container[custom_id]["groups"][group_name]["subcommands"][name]
            cls._temp_id = f"{name}*{group_name}**{custom_id}"

        elif '*' in cls._temp_id:
            custom_id = cls._temp_id.split('*')[-1]
            cls._temp_id = f'{name}*{custom_id}'
            subcommand = SubCommand(name, description)
            cls._container[custom_id]["subcommands"][name] = {
                "object": subcommand,
                "method": None,
            }
            ref = cls._container[custom_id]["subcommands"][name]

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            ref["method"] = wrapper()
            return cls
        return decorator

    @classmethod
    def group(cls, name: str, description: str):

        if '*' not in cls._temp_id:
            custom_id = cls._temp_id
        else:
            custom_id = cls._temp_id.split('*')[-1]

        cls._container[custom_id]["groups"][name] = {
            "object": SubCommandGroup(name, description),
            "subcommands": {},
            "method": None,
        }

        cls._temp_id = f'{name}**{custom_id}'

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            cls._container[custom_id]["groups"][name]["method"] = wrapper()
            return cls
        return decorator

    @classmethod
    def default_permission(cls, permission: discord.Permissions):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[cls._temp_id]["command"]["object"]._inject_permission(permission)
                return cls
            return wrapper()
        return decorator

    @classmethod
    def auto_complete(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[cls._temp_id]["command"]["autocompletes"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def check(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[cls._temp_id]["command"]["check"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def before_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[cls._temp_id]["command"]["before_invoke"] = coro
                return func
            return wrapper()
        return decorator

    @classmethod
    def after_invoke(cls, coro: Callable):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls._container[cls._temp_id]["command"]["after_invoke"] = coro
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
