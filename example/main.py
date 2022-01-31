import os
import discord
from extslash import *
from extslash.commands import Client


intents = discord.Intents.default()
intents.members = True


class MyBot(Client):
    def __init__(self):
        super().__init__(command_prefix='-', help_command=None, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()

bot.load_slash('cog.echo', 877399405056102431)
bot.run(os.getenv('DISCORD_TOKEN'))
