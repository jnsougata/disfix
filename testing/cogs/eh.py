import sys
import asyncio
import traceback
import discord
import src.app_utils as app_utils



class Error(app_utils.Cog):

    def __init__(self, bot: app_utils.Bot):
        self.bot = bot

    @app_utils.Cog.listener
    async def on_command_error(self, ctx: app_utils.Context, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await ctx.send_followup(f'```py\n{tb}\n```')

    @app_utils.Cog.command(
        command=app_utils.SlashCommand(
            name='all',
            description='get all commands',
            options=[
                app_utils.IntOption(
                    name='page',
                    description='page number',
                    max_value=10,
                    min_value=1,
                    required=True,
                )
            ]
        ),
        guild_id=877399405056102431
    )
    async def all_command(self, ctx: app_utils.Context):
        await ctx.defer()
        await self.bot.sync_global_commands()
        print(ctx.command.default_access)
        await ctx.send_followup(f'```py\n{self.bot.application_commands}\n```')

    @app_utils.Cog.command(
        command=app_utils.UserCommand(
            name='Promote It',
        ),
        guild_id=877399405056102431
    )
    async def promote_command(self, ctx: app_utils.Context):
        await ctx.send_response(f'User promoted by {ctx.author.mention}'
                                f'\n**Resolved:**```py\n{ctx.resolved.users}\n```')


def setup(bot: app_utils.Bot):
    bot.add_application_cog(Error(bot))
