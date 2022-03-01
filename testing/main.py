import os
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


bot = MyBot()
bot.load_extension('cogs.sample')
bot.load_extension('cogs.extras')
bot.run(os.getenv('DISCORD_TOKEN'))
