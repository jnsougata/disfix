from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass(frozen=True)
class Interaction:
    id: int
    version: int
    token: str
    type: int
    data: dict
    application_id: int
    guild_id: Optional[Union[int, str]] = None
    channel_id: Optional[Union[int, str]] = None
    message: Optional[dict] = None
    member: Optional[dict] = None
    user: Optional[dict] = None
    locale: Optional[str] = None
    guild_locale: Optional[str] = None


@dataclass(frozen=True)
class InteractionData:
    id: Union[int, str]
    name: str
    type: int
    resolved: Optional[dict] = None
    options: Optional[dict] = None
    # below are only used for type != 2
    custom_id: Optional[str] = None
    component_type: Optional[int] = None
    values: Optional[list] = None
    # only used for User Command & Message Command
    target_id: Optional[str] = None


@dataclass(frozen=True)
class InteractionDataOption:
    name: str
    type: int
    value: Union[str, int, float, bool] = None
    options: Optional[list] = None
    focused: Optional[bool] = None


@dataclass(frozen=True)
class InteractionDataResolved:
    # only for extslash command
    users: Optional[dict] = None
    members: Optional[dict] = None
    roles: Optional[dict] = None
    channels: Optional[dict] = None
    messages: Optional[dict] = None


@dataclass(frozen=True)
class BaseAppCommand:
    id: int
    name: str
    description: str
    type: int
    application_id: Optional[Union[int, str]]
    guild_id: Optional[Union[int, str]] = None
    options: Optional[list] = None
    default_permission: Optional[bool] = None
    version: Optional[Union[int, str]] = None
    default_member_permissions: Optional[list] = None
    dm_permission: Optional[bool] = None
    name_localizations: Optional = None
    description_localizations: Optional = None
