import os
import discord
from src.extslash.commands import Bot


intents = discord.Intents.default()
intents.members = True


class MyBot(Bot):
    def __init__(self):
        super().__init__(command_prefix='-', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()
bot.load_extension('cogs.embed')
bot.run(os.getenv('DISCORD_TOKEN'))
