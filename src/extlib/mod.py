import discord
from typing import List
from enum import Enum

__all__ = [
    'AutoModEvent',
    'AutoModTrigger',
    'ModerationRule',
    'AutoModAction',
    'KeywordPresets',
    'TriggerMetadata'
]


class AutoModEvent(Enum):
    MESSAGE_SEND = 1


class AutoModTrigger(Enum):
    KEYWORD = 1
    HARMFUL_LINK = 2
    SPAM = 3
    KEYWORD_PRESET = 4


class AutoModActionType(Enum):
    BLOCK_MESSAGE = 1
    SEND_ALERT_MESSAGE = 2
    TIMEOUT = 3


class KeywordPresets(Enum):
    PROFANITY = 1
    SEXUAL_CONTENT = 2
    SLURS = 3


class AutoModAction:

    def __init__(self, data: dict):
        self._data = data

    @classmethod
    def block_message(cls):
        return cls(
            {
                'type': AutoModActionType.BLOCK_MESSAGE.value,
                'metadata': {}
            }
        )

    @classmethod
    def send_alert_message(cls, channel_id: int):
        return cls(
            {
                'type': AutoModActionType.SEND_ALERT_MESSAGE.value,
                'metadata': {
                    'channel_id': str(channel_id)
                }
            }
        )

    @classmethod
    def timeout(cls, seconds: int):
        return cls(
            {
                'type': AutoModActionType.TIMEOUT.value,
                'metadata': {
                    'duration_seconds': seconds
                }
            }
        )


class TriggerMetadata:
    def __init__(self, value: dict):
        self._value = value

    @classmethod
    def keyword_filter(cls, keywords: List[str]):
        return cls({
            'keyword_filter': keywords
        })

    @classmethod
    def keyword_preset_filter(cls, presets: List[KeywordPresets]):
        return cls({
            'presets': [preset.value for preset in presets]
        })


class ModerationRule:

    def __init__(
            self,
            name,
            *,
            event_type: AutoModEvent,
            trigger_type: AutoModTrigger,
            enabled: bool = True,
            ignore_role_ids: List[int] = None,
            ignore_channel_ids: List[int] = None
    ):
        self._data = {
            'name': name,
            'event_type': event_type.value,
            'trigger_type': trigger_type.value,
            'actions': []
        }
        if ignore_role_ids:
            self._data['exempt_roles'] = [str(role_id) for role in ignore_role_ids]
        if ignore_channel_ids:
            self._data['exempt_channels'] = [str(channel_id) for channel in ignore_channel_ids]

    def add_action(self, action: AutoModAction):
        self._data['actions'].append(action._data)

    def add_trigger_metadata(self, metadata: TriggerMetadata):
        self._data['trigger_metadata'] = metadata._value

    def to_dict(self):
        return self._data
