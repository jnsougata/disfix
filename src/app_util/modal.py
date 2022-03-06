import os
import asyncio
import discord
from discord.utils import MISSING
from typing import Callable
from typing import Optional, Union, Any, Sequence, List, Dict
from .enums import TextInputStyle, ModalFieldStyle


class Modal:

    def __init__(self, client: discord.Client, title: str, *, custom_id: str = None):
        self.title = title
        self.client = client
        self.custom_id = custom_id or os.urandom(16).hex()
        self.data = {"title": title, "custom_id": self.custom_id, "components": []}

    def add_field(
            self,
            label: str,
            custom_id: str,
            *,
            style: TextInputStyle,
            value: str = None,
            hint: str = None,
            min_length: int = 0,
            max_length: int = 4000,
            required: bool = True,

    ):
        self.data["components"].append(
            {
                "type": 1,
                "components": [
                    {
                        "label": label,
                        "style": style.value,
                        "custom_id": custom_id,
                        "min_length": min_length,
                        "max_length": max_length,
                        "placeholder": hint or "",
                        "required": required,
                        "type": ModalFieldStyle.TEXT_INPUT.value,
                    }
                ]
            }
        )

    def to_payload(self):
        if not len(self.data['components']) > 0:
            raise ValueError("You must add at least one field to the modal")

        if len(self.data['components']) > 5:
            raise ValueError("You can only have a maximum of 5 fields in a modal")

        return {'type': 9, 'data': self.data}

    def callback(self, coro: Callable):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("callback method must be a coroutine")
        self.client._modals[self.custom_id] = coro
