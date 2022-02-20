import sys
import asyncio
import traceback
import discord
import src.app_util as app_util



class Error(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.listener
    async def on_command_error(self, ctx: app_util.Context, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await ctx.send_followup(f'```py\n{tb}\n```')

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='all',
            description='get all commands',
            options=[
                app_util.MentionalbaleOption(
                    name='mentionable',
                    description='mention user or role',
                )
            ]
        ),
        guild_id=877399405056102431
    )
    async def all_command(self, ctx: app_util.Context):
        await ctx.defer()
        await self.bot.sync_global_commands()
        print(ctx.command.default_access)
        await ctx.send_followup(f'```py\n{self.bot.application_commands}\n```')

    @app_util.Cog.command(
        command=app_util.UserCommand(
            name='Promote It',
        ),
        guild_id=877399405056102431
    )
    async def promote_command(self, ctx: app_util.Context):
        await ctx.resolved_user.send('You have been promoted! LOL')

    @app_util.Cog.command(
        command=app_util.MessageCommand(
            name='Pin',
        ),
        guild_id=877399405056102431
    )
    async def pin_command(self, ctx: app_util.Context):
        await ctx.resolved_message.pin()
        await ctx.send_response(f'Message pinned by {ctx.author.mention}')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Error(bot))
