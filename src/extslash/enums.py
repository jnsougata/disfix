from dataclasses import dataclass
from enum import Enum


class OptionType:
    SUBCOMMAND = 1
    SUBCOMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10
    ATTACHMENT = 11


@dataclass(frozen=True)
class ResolvedAttachment:
    id: str = None
    filename: str = None
    description: str = None
    content_type: str = None
    size: int = None
    url: str = None
    proxy_url: str = None
    height: int = None
    width: int = None
    ephemeral: bool = None


class ApplicationCommandType(Enum):
    USER = 2
    MESSAGE = 3
    CHAT_INPUT = 1
