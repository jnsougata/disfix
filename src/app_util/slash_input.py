from typing import Any, Union, List, Dict, Optional
from dataclasses import dataclass
from .app import Overwrite


__all__ = [
    'SlashCommand',
    'SubCommand',
    'SubCommandGroup',
    'StrOption',
    'IntOption',
    'BoolOption',
    'UserOption',
    'ChannelOption',
    'RoleOption',
    'MentionableOption',
    'NumberOption',
    'AttachmentOption',
    'Choice',
    'ChannelType',
]


@dataclass(frozen=True)
class ChannelType:
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class _Option:
    data: Any


class Choice:
    def __init__(self, name: str, value: Any):
        self.data = {
            "name": name,
            "value": value
        }


class StrOption(_Option):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 3,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class IntOption(_Option):
    def __init__(
            self, name: str,
            description: str,
            *,
            min_value: int = None,
            max_value: int = None,
            required: bool = True,
            choices: list[Choice] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 4,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }
        if min_value:
            self.data["min_value"] = min_value
        if max_value:
            self.data["max_value"] = max_value


class BoolOption(_Option):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 5,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class UserOption(_Option):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 6,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class ChannelOption(_Option):
    def __init__(
            self,
            name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None,
            channel_types: [int] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 7,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else [],
            "channel_types": channel_types if channel_types else []
        }


class RoleOption(_Option):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 8,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class MentionableOption(_Option):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 9,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class NumberOption(_Option):
    def __init__(
            self,
            name: str,
            description: str,
            *,
            min_value: float = None,
            max_value: float = None,
            required: bool = True,
            choices: list[Choice] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 10,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }
        if min_value:
            self.data["min_value"] = min_value
        if max_value:
            self.data["max_value"] = max_value


class AttachmentOption(_Option):
    def __init__(
            self,
            name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
    ):
        self.data = {
            "name": name,
            "type": 11,
            "required": required,
            "description": description,
        }


class SubCommand:
    def __init__(
            self,
            name: str,
            *,
            description: str,
            options: [_Option] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 1,
            "options": [option.data for option in options] if options else []
        }


class SubCommandGroup:
    def __init__(
            self,
            name: str,
            description: str,
            *,
            options: [SubCommand] = None
    ):
        self.data = {
            "name": name,
            "description": description,
            "type": 2,
            "options": [sc.data for sc in options] if options else []
        }


class SlashCommand:

    def __init__(
            self,
            *,
            name: str,
            description: str,
            options: List[Union[_Option, SubCommand, SubCommandGroup]] = None,
            default_access: bool = True,
            overwrites: list[Overwrite] = None,
    ) -> None:
        self._map = 'SLASH_' + name.upper()
        self._overwrites = overwrites
        self._payload = {
            "name": name,
            "description": description,
            "type": 1,
            "options": [option.data for option in options] if options else [],
            "default_permission": default_access,
        }

    @property
    def overwrites(self):
        if self._overwrites:
            return {"permissions": [perm.to_dict() for perm in self._overwrites]}

    def to_dict(self):
        return self._payload
