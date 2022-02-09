import sys
import asyncio
import traceback
import discord
import src.extslash as extslash
from src.extslash.commands import Bot, SlashCog, ApplicationContext


class Embed(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def register(self):
        return extslash.SlashCommand(
            name='embed',
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
                extslash.StrOption('thumbnail', 'url of the thumbnail to set', required=False),
                extslash.StrOption('image', 'url of the image to set', required=False),
            ],
        )

    async def command(self, ctx: ApplicationContext):
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
                slots['thumbnail'] = {'url': option.value}
            elif option.name == 'image':
                slots['image'] = {'url': option.value}
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
        await ctx.send_response(f'Embed sent successfully to {channel.mention}', ephemeral=True)


    async def on_error(self, ctx: ApplicationContext, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        print(''.join(stack), file=sys.stderr)





def setup(bot: Bot):
    bot.add_slash_cog(Embed(bot), 877399405056102431)
    # add guild if you want to limit the command to a specific guild
    # if you to register the command to all guilds, you can leave it empty
    # global commands take 1hour to register for the first time for all guilds
