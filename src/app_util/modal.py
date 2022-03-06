import asyncio
from typing import Callable
from .enums import TextInputStyle, ModalFieldStyle


class Modal:

    def __init__(self, contex, title: str):
        self.title = title
        self.ctx = contex
        self.custom_id = f'{contex.author.id}'
        self.data = {
            "title": title,
            "custom_id": self.custom_id,
            "components": []
        }

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
        return {'type': 9, 'data': self.data}

    def callback(self, func: Callable):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("callback method must be a coroutine")
        self.ctx.client._modals[self.ctx.author.id] = func
