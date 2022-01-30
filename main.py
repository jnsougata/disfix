import os
import discord
from discord.ext import commands, tasks
from src.application import *
from src.application.commands import Client, ApplicationContext


intents = discord.Intents.default()
intents.members = True


class MyBot(Client):
    def __init__(self):
        super().__init__(command_prefix='-', help_command=None, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()


bot.load_slash('cog.test', 877399405056102431)
bot.run(os.getenv('DISCORD_TOKEN'))
