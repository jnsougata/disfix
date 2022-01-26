import os
import discord
from discord.ext import commands
from src.extslash import Bot, Slash, SlashContext
from slash_cmds import *

bot = Bot(
    prefix='!',
    help_command=None,
    intents=discord.Intents.default(),
    guild_id=877399405056102431
)


@bot.slash_command(command=cmd)
async def echo(ctx: SlashContext):
    await ctx.reply(f'**{ctx.options[0].value}**')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

bot.run(os.getenv('DISCORD_TOKEN'))
