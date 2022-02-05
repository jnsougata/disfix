import os
import discord
from src.extslash.commands import Bot


intents = discord.Intents.default()
intents.members = True


class MyBot(Bot):
    def __init__(self):
        super().__init__(command_prefix='-', help_command=None, intents=intents, enable_debug_events=True)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()
bot.load_extension('cogs.echo')
bot.run(os.getenv('DISCORD_TOKEN'))
