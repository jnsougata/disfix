import sys
import asyncio
import traceback
import discord
import src.app_util as app_util


class Sample(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.listener
    async def on_command_error(self, ctx: app_util.Context, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await ctx.send_followup(f'```py\n{tb}\n```')

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='setup',
            description='configure PixeL for your Server',
            options=[
                app_util.IntOption(
                    name='remove',
                    description='remove any old configuration',
                    choices=[
                        app_util.Choice(name='youtube', value=0),
                        app_util.Choice(name='receiver', value=1),
                        app_util.Choice(name='reception', value=2),
                        app_util.Choice(name='ping_role', value=3),
                        app_util.Choice(name='welcome_card', value=4),
                        app_util.Choice(name='custom_message', value=5)
                    ],
                    required=False),
                app_util.IntOption(
                    name='overview',
                    description='overview of existing configuration',
                    choices=[
                        app_util.Choice(name='youtube', value=0),
                        app_util.Choice(name='receiver', value=1),
                        app_util.Choice(name='reception', value=2),
                        app_util.Choice(name='ping_role', value=3),
                        app_util.Choice(name='welcome_card', value=4),
                        app_util.Choice(name='custom_message', value=5)
                    ],
                    required=False),

                app_util.StrOption(
                    name='youtube',
                    description='add any youtube channel by URL / ID',
                    required=False),

                app_util.ChannelOption(
                    name='receiver',
                    description='text channel to receive youtube videos',
                    channel_types=[app_util.ChannelType.GUILD_TEXT, app_util.ChannelType.GUILD_NEWS],
                    required=False),

                app_util.ChannelOption(
                    name='reception',
                    description='text channel to receive welcome cards',
                    channel_types=[app_util.ChannelType.GUILD_TEXT, app_util.ChannelType.GUILD_NEWS],
                    required=False),

                app_util.RoleOption(
                    name='ping_role',
                    description='role to ping with youtube notification',
                    required=False),

                app_util.AttachmentOption(
                    name='welcome_card',
                    description='image file to send when new member joins',
                    required=False),

                app_util.IntOption(
                    name='custom_message',
                    description='custom welcome and notification message',
                    choices=[
                        app_util.Choice(name='upload_message', value=1),
                        app_util.Choice(name='welcome_message', value=0),
                        app_util.Choice(name='livestream_message', value=2),
                    ],
                    required=False),
            ]
        ),
        guild_id=877399405056102431
    )
    async def all_command(self, ctx: app_util.Context):
        await ctx.defer()
        await ctx.send_followup(f'```py\n{ctx.options}\n```')

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
    bot.add_application_cog(Sample(bot))
