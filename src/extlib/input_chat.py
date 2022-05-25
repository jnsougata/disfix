import discord
from typing import Any, Union, List, Dict, Optional
from .origin import ApplicationCommandOrigin
from .enums import ChannelType, CommandType, OptionType


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
]


class Option:
    """
    Represents an option for an application command
    """
    def __init__(self, name: str, type_: OptionType):
        self.name = name.lower().replace(' ', '_')
        self.type = type_


class Choice:
    """
    Represents a choice for an application command
    """
    def __init__(self, name: str, value: Any):
        self.data = {"name": name, "value": value}


class StrOption(Option):
    """
    Represents a string option for an application command
    """
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: List[Choice] = None,
            autocomplete: bool = False,
    ):
        super().__init__(name, OptionType.STRING)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices and autocomplete:
            raise ValueError("Both choices and autocomplete cannot be set together")

        if choices:
            self.data["choices"] = [c.data for c in choices]
        if autocomplete:
            self.data["autocomplete"] = autocomplete


class IntOption(Option):
    """
    Represents an integer option for an application command
    """
    def __init__(
            self, name: str,
            description: str,
            *,
            min_value: int = None,
            max_value: int = None,
            required: bool = True,
            choices: List[Choice] = None,
            autocomplete: bool = False
    ):
        super().__init__(name, OptionType.INTEGER)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices and autocomplete:
            raise ValueError("Both choices and autocomplete cannot be set together")

        if choices:
            self.data["choices"] = [c.data for c in choices]
        if autocomplete:
            self.data["autocomplete"] = autocomplete
        if min_value:
            self.data["min_value"] = min_value
        if max_value:
            self.data["max_value"] = max_value


class BoolOption(Option):
    """
    Represents a boolean option for an application command
    """
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: List[Choice] = None,
    ):
        super().__init__(name, OptionType.BOOLEAN)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices:
            self.data["choices"] = [c.data for c in choices]


class UserOption(Option):
    """
    Represents a user option for an application command
    """
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: List[Choice] = None
    ):
        super().__init__(name, OptionType.USER)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices:
            self.data["choices"] = [c.data for c in choices]


class ChannelOption(Option):
    """
    Represents a channel option for an application command
    """
    def __init__(
            self,
            name: str,
            description: str,
            *,
            required: bool = True,
            choices: List[Choice] = None,
            channel_types: [ChannelType] = None
    ):
        super().__init__(name, OptionType.CHANNEL)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices:
            self.data["choices"] = [c.data for c in choices]
        if channel_types:
            self.data["channel_types"] = [t.value for t in channel_types]


class RoleOption(Option):
    """
    Represents a role option for an application command
    """
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: List[Choice] = None
    ):
        super().__init__(name, OptionType.ROLE)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices:
            self.data["choices"] = [c.data for c in choices]


class MentionableOption(Option):
    """
    Represents a mentionable option for an application command
    """
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: List[Choice] = None
    ):
        super().__init__(name, OptionType.MENTIONABLE)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices:
            self.data["choices"] = [c.data for c in choices]


class NumberOption(Option):
    """
    Represents a number option for an application command
    """
    def __init__(
            self,
            name: str,
            description: str,
            *,
            min_value: Union[float, int] = None,
            max_value: Union[float, int] = None,
            required: bool = True,
            choices: List[Choice] = None,
            autocomplete: bool = False
    ):
        super().__init__(name, OptionType.NUMBER)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices and autocomplete:
            raise ValueError("Both choices and autocomplete cannot be set together")

        if choices:
            self.data["choices"] = [c.data for c in choices]
        if min_value:
            self.data["min_value"] = min_value
        if max_value:
            self.data["max_value"] = max_value
        if autocomplete:
            self.data["autocomplete"] = autocomplete


class AttachmentOption(Option):
    """
    Represents an attachment option for an application command
    """
    def __init__(
            self,
            name: str,
            description: str,
            *,
            required: bool = True,
    ):
        super().__init__(name, OptionType.ATTACHMENT)
        self.data = {
            "name": self.name,
            "type": self.type.value,
            "required": required,
            "description": description,
        }


class SubCommand:
    """
    Represents a sub-command for an application command
    """
    def __init__(
            self,
            name: str,
            description: str,
            *,
            options: [Option] = None
    ):
        self.name = name.lower().replace(' ', '_')
        self.type = OptionType.SUBCOMMAND
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
        }
        if options:
            self.data["options"] = [op.data for op in options]


class SubCommandGroup(Option):
    """
    Represents a sub-command group for an application command
    """
    def __init__(
            self,
            name: str,
            description: str,
            *,
            options: [SubCommand] = None
    ):
        super().__init__(name, OptionType.SUBCOMMAND_GROUP)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
        }
        if options:
            self.data["options"] = [sc.data for sc in options]


class SlashCommand(ApplicationCommandOrigin):
    """
    Represents a Slash Command
    """

    def __init__(
            self,
            name: str,
            description: str,
            *,
            options: List[Union[
                IntOption,
                StrOption,
                BoolOption,
                AttachmentOption,
                MentionableOption,
                NumberOption,
                RoleOption,
                ChannelOption,
                UserOption
            ]] = None,
            dm_access: bool = True,
    ) -> None:
        fmt_name = name.lower().replace(' ', '_')
        self._payload = {
            "name": fmt_name,
            "type": None,
            "description": description,
            "dm_permission": dm_access,
            "options": [option.data for option in options] if options else [],
            "default_member_permissions": None,
        }
        super().__init__(name=fmt_name, payload=self._payload, command_type=CommandType.SLASH)
