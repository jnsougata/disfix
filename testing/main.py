import os
import discord
import src.disfix as extlib


intents = discord.Intents.default()


class Bot(disfix.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        await self.load_extension('cogs.sample')


bot = Bot()
bot.run(os.getenv('DISCORD_TOKEN'))
