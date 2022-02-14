import sys
import asyncio
import traceback
import discord
import src.extslash as extslash
from src.extslash.commands import Bot, SlashCog, ApplicationContext


class Modal(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def register(self):
        return extslash.SlashCommand(
            name='modal',
            description='testing a modal',
        )

    async def command(self, ctx: ApplicationContext):
        payload = {
                    "title": "Zen\'s Cool Modal",
                    "custom_id": "cool_modal",
                    "components": [
                        {
                            "type": 1,
                            "components": [
                                {
                                    "type": 4,
                                    "custom_id": "name",
                                    "label": "Name",
                                    "style": 1,
                                    "min_length": 1,
                                    "max_length": 4000,
                                    "placeholder": "Enter your name",
                                    "required": True
                                }
                            ]
                        },
                        {
                            "type": 1,
                            "components": [
                                {
                                    "type": 4,
                                    "custom_id": "about",
                                    "label": "About",
                                    "style": 1,
                                    "min_length": 1,
                                    "max_length": 4000,
                                    "placeholder": "Tell us something about you",
                                    "required": True
                                }
                            ]
                        }

                    ]
        }
        await ctx.send_modal(payload=payload)


    async def on_error(self, ctx: ApplicationContext, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        print(''.join(stack), file=sys.stderr)



def setup(bot: Bot):
    bot.add_slash_cog(Modal(bot), 877399405056102431)
