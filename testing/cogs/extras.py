import sys
import asyncio
import traceback
import discord
import src.app_util as app_util


class Extras(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.listener
    async def on_command_error(self, ctx: app_util.Context, error: Exception):
        print(error.__class__.__name__, file=sys.stderr)
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        print(tb, file=sys.stderr)
        await ctx.send_followup(f'Traceback printed in terminal!')


    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='global',
            description='placeholder global command',
        )
    )
    async def global_command(self, ctx: app_util.Context):
        await ctx.send_response(f'You have successfully used a Global Application Command')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Extras(bot))
