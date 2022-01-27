import os
import discord
from discord.ext import commands, tasks
from src.extslash import SlashBot, Slash, SlashContext
from cmds import echo


intents = discord.Intents.default()


class MyBot(SlashBot):
    def __init__(self):
        super().__init__(prefix='-', help_command=None, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()


@bot.slash_command(command=echo)
async def echo(ctx: SlashContext):
    await ctx.respond(embed=discord.Embed(description=f'**{ctx.options[0].value}**'), ephemeral=True)


bot.load_extension('cogs.example')
bot.run(os.getenv('DISCORD_TOKEN'))
