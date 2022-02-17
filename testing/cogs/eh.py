import sys
import asyncio
import traceback
import discord
import src.extslash as extslash



class Error(extslash.Cog):

    def __init__(self, bot: extslash.Bot):
        self.bot = bot

    @extslash.Cog.listener
    async def on_command_error(self, ctx: extslash.ApplicationContext, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await ctx.send_followup(f'```py\n{tb}\n```')

    @extslash.Cog.command(
        command=extslash.SlashCommand(
            name='xcog',
            description='accessing from same slash cog'
        ),
        guild_id=877399405056102431
    )
    async def xcog(self, ctx: extslash.ApplicationContext):
        await ctx.send_response(f'hello {self.bot.user.id}')


def setup(bot: extslash.Bot):
    bot.add_slash_cog(Error(bot))
