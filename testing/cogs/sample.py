import os
import sys
import asyncio
import traceback
import discord
import aiohttp
from aiotube import Search
import src.app_util as app_util


async def check(ctx: app_util.Context):
    if not ctx.guild:
        await ctx.send_response(f'{ctx.author.mention} please use command `{ctx.name}` inside a guild')
    elif not ctx.author.guild_permissions.administrator:
        await ctx.send_response(f'{ctx.author.mention} you are not an administrator')
    elif not ctx.options:
        await ctx.send_response(f'{ctx.author.mention} please select any valid option')
    else:
        return True


async def send_autocomplete(ctx: app_util.Context, channel: str):
    if channel:
        channels = Search.channels(channel, limit=5)
        urls = channels.urls
        names = channels.names
        choices = [app_util.Choice(name=ch_name, value=url) for ch_name, url in zip(names, urls)]
        await ctx.send_automated_choices(choices)


class Sample(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.before_invoke(autocomplete_handler=send_autocomplete)
    @app_util.Cog.command(
        app_util.SlashCommand(
            name='find',
            description='find YouTube channels by name',
            options=[
                app_util.StrOption(name='channel', description='channel name to search', autocomplete=True),
            ]
        ),
        guild_id=877399405056102431
    )
    async def autocomplete_command(self, ctx: app_util.Context, channel: str):
        await ctx.send_response(f'You\'ve picked the channel `{channel}`')

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='embed',
            description='creates an embed to current channel',
            options=[
                app_util.StrOption('title', 'title of the embed', required=False),
                app_util.StrOption('description', 'description of the embed', required=False),
                app_util.StrOption('url', 'hyperlink url of the title', required=False),
                app_util.StrOption('color', 'color hex of the embed', required=False),
                app_util.UserOption('author', 'author of the embed', required=False),
                app_util.StrOption('author_url', 'hyperlink url of the author', required=False),
                app_util.AttachmentOption('thumbnail', 'image file of thumbnail', required=False),
                app_util.AttachmentOption('image', 'image file to add to embed', required=False),
                app_util.StrOption('footer_text', 'footer text of the embed', required=False),
                app_util.AttachmentOption('footer_icon', 'file for embed', required=False),
                app_util.StrOption('link_button', 'sends a link in button form with embed', required=False),
            ],
        ),
        guild_id=877399405056102431
    )
    @app_util.Cog.before_invoke(check=check)
    async def embed(
            self,
            ctx: app_util.Context,
            *,
            title: str, description: str, url: str,
            color: str, author: discord.User, author_url: str,
            thumbnail: discord.Attachment, image: discord.Attachment,
            footer_icon: discord.Attachment, footer_text: str, link_button: str,
    ):
        await ctx.defer(ephemeral=True)
        slots = {}
        if title:
            slots['title'] = title
        if footer_text:
            slots['footer'] = {'text': footer_text}
            if footer_icon:
                slots['footer']['icon_url'] = footer_icon.url
        if description:
            slots['description'] = description.replace('$/', '\n')
        if url:
            slots['url'] = url
        if color:
            slots['color'] = int(color, 16)
        if author:
            slots['author'] = {
                'name': author.name,
                'icon_url': author.avatar.url,
            }
            if author_url:
                slots['author']['url'] = author_url
        if thumbnail:
            slots['thumbnail'] = {'url': thumbnail.url}
        if image:
            slots['image'] = {'url': image.url}

        view = discord.ui.View()

        if link_button:
            button = discord.ui.Button(style=discord.ButtonStyle.link, label='link', url=link_button)
            view.add_item(button)

        embed = discord.Embed.from_dict(slots)
        await ctx.channel.send(embed=embed, view=view)
        await ctx.send_followup(f'Embed sent successfully')


    @app_util.Cog.command(
        command=app_util.UserCommand(name='Bonk'),
        guild_id=877399405056102431
    )
    async def promote_command(self, ctx: app_util.Context, user: discord.User):
        await ctx.send_response(f'{user.mention} **{ctx.author}** just bonked you', delete_after=5)

    @app_util.Cog.command(
        command=app_util.MessageCommand(name='Pin'),
        guild_id=877399405056102431
    )
    async def pin_command(self, ctx: app_util.Context, message: discord.Message):
        await message.pin()
        await ctx.send_response(f'Message pinned by {ctx.author.mention}')

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='modal',
            description='sends a placeholder modal',
        ),
        guild_id=877399405056102431
    )
    async def modal_command(self, ctx: app_util.Context, name: str):

        modal = app_util.Modal(client=self.bot, title=f'A Super Modal for {ctx.author.name}')
        modal.add_field(
            label='About',
            custom_id='about',
            style=app_util.ModalTextType.LONG,
            required=False,
            hint='Write something about yourself...',
        )
        modal.add_field(
            label='Tip',
            custom_id='tip',
            style=app_util.ModalTextType.SHORT,
            required=True,
            hint='Give me some tips to improve...',
            max_length=100,
        )
        await ctx.send_modal(modal)

        @modal.callback
        async def on_submit(mcx: app_util.Context, about: str, tip: str):
            embed = discord.Embed(
                description=f'**About:** {about}\n**Tip:** {tip}')
            embed.set_author(name=f'{mcx.author.name}', icon_url=mcx.author.avatar.url)
            await mcx.send_response(embed=embed)


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Sample(bot))
