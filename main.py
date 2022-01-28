import os
import discord
from discord.ext import commands, tasks
from src.extslash import SlashBot, Slash, SlashInteraction
from cmds import setup, setup_command


intents = discord.Intents.default()
intents.members = True


class MyBot(SlashBot):
    def __init__(self):
        super().__init__(prefix='-', help_command=None, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()
bot.add_slash(setup, setup_command, 877399405056102431)
bot.run(os.getenv('DISCORD_TOKEN'))
