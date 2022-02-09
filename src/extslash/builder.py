from typing import Any, Union, List, Dict, Optional
from dataclasses import dataclass


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
    def __init__(self, name: str, description: str, required: bool = True, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 3,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class IntOption(_Option):
    def __init__(self, name: str, description: str, required: bool = True, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 4,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class BoolOption(_Option):
    def __init__(self, name: str, description: str, required: bool = True, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 5,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class UserOption(_Option):
    def __init__(self, name: str, description: str, required: bool = True, choices: list[Choice] = None):
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
    def __init__(self, name: str, description: str, required: bool = True, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 8,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class MentionableOption(_Option):
    def __init__(self, name: str, description: str, required: bool = True, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 9,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class NumberOption(_Option):
    def __init__(self, name: str, description: str, required: bool = True, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 10,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class AttachmentOption(_Option):
    def __init__(self, name: str, description: str, required: bool = True, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "type": 11,
            "required": required,
            "description": description,
        }


class SubCommand:
    def __init__(self, name: str, description: str, options: [_Option] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 1,
            "options": [option.data for option in options] if options else []
        }


class SubCommandGroup:
    def __init__(self, name: str, description: str, options: [SubCommand] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 2,
            "options": [sc.data for sc in options] if options else []
        }


class SlashPermission:
    def __init__(self, payload: dict):
        self._payload = payload

    def to_dict(self):
        return self._payload

    @classmethod
    def for_role(cls, role_id: int, allow: bool = True):
        return cls({
            'id': str(role_id),
            'type': 1,
            'permission': allow
        })

    @classmethod
    def for_user(cls, user_id: int, allow: bool = True):
        return cls({
            'id': str(user_id),
            'type': 2,
            'permission': allow
        })


class SlashCommand:

    def __init__(
            self,
            name: str,
            description: str,
            options: list[Union[_Option, SubCommand, SubCommandGroup, Choice]] = None,
            everyone: bool = True,
            permissions: list[SlashPermission] = None,
    ) -> None:
        self.name = name
        self._payload = {
            "name": name,
            "description": description,
            "type": 1,
            "options": [option.data for option in options] if options else [],
            "default_permission": everyone,
        }
        self._permissions = permissions

    @property
    def permissions(self):
        if self._permissions:
            perms_list = [perm.to_dict() for perm in self._permissions]
            return {"permissions": perms_list}

    def to_dict(self):
        return self._payload
