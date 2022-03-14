import os
import asyncio
import discord
import src.app_util as app


intents = discord.Intents.default()
intents.members = True


class MyBot(app.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        await self.load_extension('cogs.sample')


bot = MyBot()
bot.run(os.getenv('DISCORD_TOKEN'))
