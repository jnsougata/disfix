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
    elif not ctx.options:
        await ctx.send_response(f'{ctx.author.mention} please select any valid option')
    else:
        return True


class Sample(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot


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
    @app_util.Cog.before_invoke(job)
    async def embed(
            self,
            ctx: app_util.Context,
            *,
            title: str, description: str, url: str,
            color: str, author: discord.User, author_url: str,
            thumbnail: discord.Attachment, image: discord.Attachment,
            footer_icon: discord.Attachment, footer_text: str, link_button: str,
    ):
        async with ctx.thinking(5, author_only=True):
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
        modal = app_util.Modal(
            contex=ctx,
            title=f'A Super Modal for {ctx.author.name}',
        )
        modal.add_field(
            label='About',
            custom_id=str(ctx.author.id),
            style=app_util.TextInputStyle.PARAGRAPH,
            required=True,
            hint='Write something about yourself...'
        )
        await ctx.send_modal(modal)

        @modal.callback
        async def on_submit(interaction: discord.Interaction):
            embed = discord.Embed(
                description=f'**{ctx.author}** just used a modal\n\n**Modal Data:**\n```{interaction.data}```')
            await interaction.response.send_message(embed=embed)


def setup(bot: app_util.Bot):
    bot.add_application_cog(Sample(bot))
