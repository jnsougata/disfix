import sys
import asyncio
import traceback
import discord
import src.extslash as extslash



class Error(extslash.Cog):

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
    async def cog_command(self, ctx: extslash.ApplicationContext):
        print(1/0)
        await ctx.send_response('hello')


def setup(bot: extslash.Bot):
    bot.add_slash_cog(Error())
