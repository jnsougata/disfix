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


@bot.slash_command(command=cmd_one)
async def slash(ctx: SlashContext):
    emd = discord.Embed(
        title=f'Slash Command | [{ctx.name}]',
        description=f'`member` ```{ctx.member}```'
    )
    await ctx.reply(embed=emd)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print('------')

bot.run(os.getenv('DISCORD_TOKEN'))
