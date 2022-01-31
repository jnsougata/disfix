from typing import Any, Union, List, Dict, Optional


class _Option:
    data: Any


class Choice:
    def __init__(self, name: str, value: Any):
        self.data = {
            "name": name,
            "value": value
        }


class StrOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 3,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class IntOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 4,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class BoolOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 5,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class UserOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 6,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class ChannelOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 7,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class RoleOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 8,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class MentionableOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 9,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class NumberOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 10,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
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


class SlashCommand:

    def __init__(self, name: str, description: str, options: list[Union[_Option, SubCommand, SubCommandGroup]] = None):
        self.name = name
        self._payload = {
            "name": name,
            "description": description,
            "type": 1,
            "options": [option.data for option in options] if options else []
        }

    def to_dict(self):
        return self._payload