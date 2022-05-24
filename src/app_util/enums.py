from enum import Enum


def try_enum(enum_class, value):
    try:
        return enum_class(value)
    except ValueError:
        return None


class ModalTextType(Enum):
    SHORT = 1
    LONG = 2


class ModalFieldType(Enum):
    TEXT_INPUT = 4


class ApplicationCommandType(Enum):
    SLASH = 1
    USER = 2
    MESSAGE = 3


class OptionType(Enum):
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


class ChannelType(Enum):
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
