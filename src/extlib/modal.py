import os
import asyncio
import discord
from functools import wraps
from typing import Callable
from discord.utils import MISSING
from typing import Optional, Union, Any, Sequence, List, Dict
from .enums import ModalTextType, ModalFieldType, InteractionCallbackType, ComponentType


class Modal:
    """
    Represents a modal. This is a class that can be used to create a modal.
    """

    def __init__(self, title: str, *, custom_id: str = None):
        self.title = title
        self.custom_id = custom_id or os.urandom(16).hex()
        self.__action_row = {"type": ComponentType.ACTION_ROW.value, "components": []}
        self.data = {"title": title, "custom_id": self.custom_id, "components": []}

    def add_component(self, component: Union[discord.ui.Select, discord.ui.Button]):
        """
        Adds a select menu to the modal.
        """
        self.__action_row["components"].append(component.to_component_dict())

    def add_field(
            self,
            label: str,
            custom_id: str,
            *,
            required: bool = False,
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
                "type": ComponentType.ACTION_ROW.value,
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
        if self.__action_row["components"]:
            self.data['components'].append(self.__action_row)

        if not len(self.data['components']) > 0:
            raise ValueError("You must add at least one field to the modal")

        if len(self.data['components']) > 5:
            raise ValueError("You can only have a maximum of 5 fields in a modal")

        return {'type': InteractionCallbackType.MODAL_RESPONSE.value, 'data': self.data}

    def callback(self, client: discord.Client):
        """
        A decorator that adds a callback function to the modal.
        That coroutine callback function will be called when the modal is submitted.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            callback = wrapper()
            if not asyncio.iscoroutinefunction(callback):
                raise TypeError("callback must be a coroutine")
            client._modals[self.custom_id] = callback
            return self
        return decorator
