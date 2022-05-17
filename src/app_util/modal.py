import os
import asyncio
import discord
from typing import Callable
from discord.utils import MISSING
from .enums import ModalTextType, ModalFieldType
from typing import Optional, Union, Any, Sequence, List, Dict


class Modal:
    """
    Represents a modal. This is a class that can be used to create a modal.
    """

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
            required: bool = True,
            hint: str = None,
            default_text: str = None,
            min_length: int = 0,
            max_length: int = 4000,
            style: ModalTextType = ModalTextType.SHORT
    ):
        """
        Adds a field to the modal. Max allowed fields is 5.
        """
        if max_length > 4000:
            raise ValueError("Maximum 4000 characters is allowed")
        if min_length < 0:
            raise ValueError("Minimum 0 characters is allowed")

        self.data["components"].append(
            {
                "type": 1,
                "components": [
                    {
                        "label": label,
                        "style": style.value,
                        "value": default_text,
                        "custom_id": custom_id,
                        "min_length": min_length,
                        "max_length": max_length,
                        "placeholder": hint or "",
                        "required": required,
                        "type": ModalFieldType.TEXT_INPUT.value,
                    }
                ]
            }
        )

    def to_payload(self):
        """
        Returns the modal in json format. Internal use only.
        """
        if not len(self.data['components']) > 0:
            raise ValueError("You must add at least one field to the modal")

        if len(self.data['components']) > 5:
            raise ValueError("You can only have a maximum of 5 fields in a modal")

        return {'type': 9, 'data': self.data}

    def callback(self, coro: Callable):
        """
        A decorator that adds a callback function to the modal.
        That coroutine callback function will be called when the modal is submitted.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("callback method must be a coroutine")
        self.client._modals[self.custom_id] = coro
