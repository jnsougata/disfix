import sys
import asyncio
import traceback
import discord
import src.app_util as app_util


class Embed(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='embed',
            description='creates an embed to a channel',
            options=[
                app_util.ChannelOption(
                    name='channel',
                    description='text channel to send the embed to',
                    channel_types=[app_util.ChannelType.GUILD_TEXT],
                    required=True),
                app_util.StrOption('title', 'title of the embed', required=False),
                app_util.StrOption('description', 'description of the embed', required=False),
                app_util.StrOption('url', 'url of the embed', required=False),
                app_util.StrOption('color', 'color hex of the embed', required=False),
                app_util.UserOption('author', 'author of the embed', required=False),
                app_util.StrOption('footer', 'footer text of the embed', required=False),
                app_util.AttachmentOption('thumbnail', 'image file for thumbnail', required=False),
                app_util.AttachmentOption('image', 'image file for embed image', required=False),
            ],
            overwrites=[app_util.Overwrite.for_role(879281380306067486)],
        ),
        guild_id=877399405056102431
    )
    async def embed(self, ctx: app_util.Context):
        await ctx.defer(ephemeral=True)
        channel = ctx.options['channel'].value
        slots = {}
        for name, option in ctx.options.items():
            special = [
                'author',
                'footer',
                'thumbnail',
                'image',
                'color',
                'description'
            ]
            if name not in special:
                slots[name] = option.value
            elif name == 'footer':
                slots['footer'] = {'text': option.value}
            elif name == 'thumbnail':
                slots['thumbnail'] = {'url': option.value.url}
            elif name == 'image':
                slots['image'] = {'url': option.value.url}
            elif name == 'color':
                slots['color'] = int(f'0x{option.value}', 16)
            elif name == 'author':
                slots['author'] = {
                    'name': option.value.name,
                    'icon_url': option.value.avatar.url
                }
            elif name == 'description':
                string = option.value.replace('$/', '\n')
                slots['description'] = string

        embed = discord.Embed.from_dict(slots)
        await channel.send(embed=embed)
        await ctx.send_followup(f'Embed sent successfully to {channel.mention}')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Embed(bot))
