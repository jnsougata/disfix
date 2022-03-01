from typing import Any, Union, List, Dict, Optional
from .app import Overwrite, BaseApplicationCommand
from .enums import ChannelType, ApplicationCommandType, OptionType


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


class BaseOption:
    def __init__(self, name: str, type: OptionType):
        self.name = name.lower().replace(' ', '_')
        self.type = type


class Choice:
    def __init__(self, name: str, value: Any):
        self.data = {
            "name": name,
            "value": value
        }


class StrOption(BaseOption):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
    ):
        super().__init__(name, OptionType.STRING)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices:
            self.data["choices"] = [c.data for c in choices]


class IntOption(BaseOption):
    def __init__(
            self, name: str,
            description: str,
            *,
            min_value: int = None,
            max_value: int = None,
            required: bool = True,
            choices: list[Choice] = None
    ):
        super().__init__(name, OptionType.INTEGER)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices:
            self.data["choices"] = [c.data for c in choices]
        if min_value:
            self.data["min_value"] = min_value
        if max_value:
            self.data["max_value"] = max_value


class BoolOption(BaseOption):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
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


class UserOption(BaseOption):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
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


class ChannelOption(BaseOption):
    def __init__(
            self,
            name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None,
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


class RoleOption(BaseOption):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
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


class MentionableOption(BaseOption):
    def __init__(
            self, name: str,
            description: str,
            *,
            required: bool = True,
            choices: list[Choice] = None
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


class NumberOption(BaseOption):
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
        super().__init__(name, OptionType.NUMBER)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
            "required": required,
        }
        if choices:
            self.data["choices"] = [c.data for c in choices]
        if min_value:
            self.data["min_value"] = min_value
        if max_value:
            self.data["max_value"] = max_value


class AttachmentOption(BaseOption):
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


class SubCommand(BaseOption):
    def __init__(
            self,
            name: str,
            *,
            description: str,
            options: [BaseOption] = None
    ):
        super().__init__(name, OptionType.SUBCOMMAND)
        self.data = {
            "name": self.name,
            "description": description,
            "type": self.type.value,
        }
        if options:
            self.data["options"] = [op.data for op in options]


class SubCommandGroup(BaseOption):
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


class SlashCommand(BaseApplicationCommand):

    def __init__(
            self,
            *,
            name: str,
            description: str,
            options: List[Union[BaseOption, SubCommand, SubCommandGroup]] = None,
            default_access: bool = True,
            overwrites: list[Overwrite] = None,
    ) -> None:
        fmt_name = name.lower().replace(' ', '_')
        super().__init__(fmt_name, ApplicationCommandType.CHAT_INPUT)
        self._qual = '__CHAT__' + name
        self._overwrites = overwrites
        self._payload = {
            "name": fmt_name,
            "description": description,
            "type": self.type.value,
            "options": [option.data for option in options] if options else [],
            "default_permission": default_access,
        }

    @property
    def overwrites(self):
        if self._overwrites:
            return {"permissions": [perm.to_dict() for perm in self._overwrites]}

    def to_dict(self):
        return self._payload
