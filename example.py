import os
import discord
from discord.ext import commands
from src.extslash import SlashBot, Slash, SlashContext
from cmds import echo


intents = discord.Intents.default()


class MyBot(SlashBot):
    def __init__(self):
        super().__init__(prefix='-', help_command=None, intents=intents, guild_id=877399405056102431)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()


@bot.slash_command(command=echo)
async def echo(ctx: SlashContext):
    file = discord.File(f'example.py', filename='example.py')
    await ctx.respond(f'**{ctx.options[0].value}**', file=file, ephemeral=True)


@bot.command(name='ping')
async def ping(ctx: commands.Context):
    await ctx.reply(f'Pong: {bot.latency * 1000}ms')


bot.run(os.getenv('DISCORD_TOKEN'))
