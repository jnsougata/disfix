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
        await ctx.send_followup(f'Traceback printed in Console')


    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='perms',
            description='gives permission for role or user',
            options=[
                app_util.SubCommand(
                    name='get',
                    description='the role or user  to get the perms for',
                    options=[
                        app_util.UserOption(name='user', description='user to get the perms for', required=False),
                        app_util.RoleOption(name='role', description='role to get the perms for', required=False)
                    ]

                )
            ]
        ),
        guild_id=877399405056102431
    )
    async def sub_application_command(self, ctx: app_util.Context, get_user: discord.User, get_role: discord.Role):
        await ctx.send_response(f'Selected user `{get_user}` and role `@{get_role}`')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Extras(bot))
