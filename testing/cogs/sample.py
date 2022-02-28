import sys
import asyncio
import traceback
import discord
import src.app_util as app_util


async def job(ctx: app_util.Context):
    if not ctx.guild:
        await ctx.send_response(f'{ctx.author.mention} please use command `{ctx.name}` inside a guild')
    elif not ctx.author.guild_permissions.administrator:
        await ctx.send_response(f'{ctx.author.mention} you are not an administrator')
    else:
        return True


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
            name='global',
            description='placeholder global command',
        )
    )
    async def global_command(self, ctx: app_util.Context):
        await ctx.send_response(f'You have successfully used a Global Application Command')


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
            ],
        ),
        guild_id=877399405056102431
    )
    async def embed(
            self,
            ctx: app_util.Context,
            *,
            title: str, description: str, url: str,
            color: str, author: discord.User, author_url: str,
            thumbnail: discord.Attachment, image: discord.Attachment,
            footer_icon: discord.Attachment, footer_text: str
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

        embed = discord.Embed.from_dict(slots)
        await ctx.channel.send(embed=embed)
        await ctx.send_followup(f'Embed sent successfully')


    @app_util.Cog.command(
        command=app_util.UserCommand(name='Bonk'),
        guild_id=877399405056102431
    )
    async def promote_command(self, ctx: app_util.Context):
        await ctx.send_response(f'LOL! {ctx.clicked_user.mention} '
                                f'you have been bonked by {ctx.author.mention}')

    @app_util.Cog.command(
        command=app_util.MessageCommand(name='Pin'),
        guild_id=877399405056102431
    )
    async def pin_command(self, ctx: app_util.Context):
        print(ctx.command.type)
        await ctx.clicked_message.pin()
        await ctx.send_response(f'Message pinned by {ctx.author.mention}')

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='delete',
            description='deletes an existing application command',
            options=[
                app_util.StrOption('name', 'name of command to delete', required=True),
            ],
        ),
        guild_id=877399405056102431
    )
    @app_util.Cog.before_invoke(job=job)
    async def delete_command(self, ctx: app_util.Context, name: str):
        await ctx.defer()
        await self.bot.sync_guild_commands(ctx.guild)
        for command in self.bot.application_commands:
            if command.name == name:
                await command.delete()
                await ctx.send_followup(f'Application Command **`{name}`** has been deleted | (ID: {command.id})')
        else:
            await ctx.send_followup(f'Application Command **`{name}`** does not exist')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Sample(bot))
