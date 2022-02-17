import sys
import asyncio
import traceback
import discord
import src.extslash as extslash


class Embed(extslash.Cog):

    def __init__(self, bot: extslash.Bot):
        self.bot = bot

    @extslash.Cog.command(
        command=extslash.SlashCommand(
            name='xembed',
            description='creates an embed to a channel',
            options=[
                extslash.ChannelOption(
                    name='channel',
                    description='text channel to send the embed to',
                    channel_types=[extslash.ChannelType.GUILD_TEXT],
                    required=True),
                extslash.StrOption('title', 'title of the embed', required=False),
                extslash.StrOption('description', 'description of the embed', required=False),
                extslash.StrOption('url', 'url of the embed', required=False),
                extslash.StrOption('color', 'color hex of the embed', required=False),
                extslash.UserOption('author', 'author of the embed', required=False),
                extslash.StrOption('footer', 'footer text of the embed', required=False),
                extslash.AttachmentOption('thumbnail', 'image file for thumbnail', required=False),
                extslash.AttachmentOption('image', 'image file for embed image', required=False),
            ],
            overwrites=[extslash.SlashOverwrite.for_role(879281380306067486)],
        ),
        guild_id=None
    )
    async def embed(self, ctx: extslash.ApplicationContext):
        await ctx.defer(ephemeral=True)
        slots = {}
        channel = ctx.options[0].value
        ctx.options.pop(0)
        for option in ctx.options:
            special = ['author', 'footer', 'thumbnail', 'image', 'color', 'description']
            name = option.name
            if name not in special:
                slots[option.name] = option.value
            elif option.name == 'footer':
                slots['footer'] = {'text': option.value}
            elif option.name == 'thumbnail':
                slots['thumbnail'] = {'url': option.value.url}
            elif option.name == 'image':
                slots['image'] = {'url': option.value.url}
            elif option.name == 'color':
                slots['color'] = int(f'0x{option.value}', 16)
            elif option.name == 'author':
                slots['author'] = {
                    'name': option.value.name,
                    'icon_url': option.value.avatar.url
                }
            elif option.name == 'description':
                string = option.value.replace('$/', '\n')
                slots['description'] = string

        embed = discord.Embed.from_dict(slots)
        await channel.send(embed=embed)
        await ctx.send_followup(f'Embed sent successfully to {channel.mention}')


    @extslash.Cog.command(
        command=extslash.SlashCommand(
            name='cog',
            description='accessing from same slash cog'
        ),
        guild_id=877399405056102431
    )
    async def cog_command(self, ctx: extslash.ApplicationContext):
        await ctx.send_response('hello')
        resp = await ctx.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        await ctx.send_followup(f'{resp.content}')


def setup(bot: extslash.Bot):
    bot.add_slash_cog(Embed(bot))
