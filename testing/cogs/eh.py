import sys
import asyncio
import traceback
import discord
import src.extslash as extslash
from src.extslash import commands
from src.extslash.commands import Bot, SlashCog, ApplicationContext


class Error(commands.SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.SlashCog.listener
    async def on_slash_error(self, ctx: ApplicationContext, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await ctx.send_followup(f'```py\n{tb}\n```')


def setup(bot: Bot):
    bot.add_slash_cog(Error(bot))
