import os
import discord
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

bot.load_slash_extension('cogs.echo')
bot.run(os.getenv('DISCORD_TOKEN'))
