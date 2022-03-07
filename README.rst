app-util
==========

Asynchronous Application Command wrapper for discord.py 2.0

Installing
----------

**Python 3.8 or higher is required**

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U app-util

    # Windows
    py -3 -m pip install -U app-util

Quick Example
--------------

.. code:: py

    import discord
    import app_util


    intents = discord.Intents.default()


    class SampleBot(app_util.Bot):
        def __init__(self):
            super().__init__(command_prefix='-', intents=intents)

        async def on_ready(self):
            print(f'Logged in as {self.user} (ID: {self.user.id})')
            print('------')

    bot = SampleBot()

    bot.load_extension('extension_name')
    bot.run('YOUR_TOKEN')

Cog Example
~~~~~~~~~~~~~

.. code:: py

    import sys
    import asyncio
    import traceback
    import discord
    import app_util


    class Sample(app_util.Cog):

        def __init__(self, bot: app_util.Bot):
            self.bot = bot

        # slash command named `book`
        @app_util.Cog.command(
            command=app_util.SlashCommand(
                name='book',
                description='get a sample book',
                options=[
                    app_util.StrOption(
                        name='book_name',
                        description='the name of the book you want to get',
                        required=True,
                    ),
                    app_util.IntOption(
                        name='page',
                        description='the page number to look for',
                        max_value=10,
                        min_value=1,
                        required=True,
                    )
                ]
            ),
            guild_id=1234567890
            # if None, available for all guilds
        )
        async def book(self, ctx: app_util.Context, book_name: str, page: int):
            await ctx.defer(ephemeral=True)
            page_content = await imaginary_api.fetch(book_name, page)
            embed = discord.Embed(
                title=f'{book_name}',
                description=page_content,
                color=ctx.author.color
            )
            embed.set_footer(text=f'Page {page_number}')
            await ctx.send_followup(embed=embed)

        # user command named `Bonk`
        @app_util.Cog.command(
            command=app_util.UserCommand(name='Bonk'),
            # guild_id not given, available for all guilds
        )
        async def bonk(self, ctx: app_util.Context, user: discord.User):
            await ctx.send_response(f'{ctx.author.mention} just bonked {user.mention}!')

        # message command named `Pin`
        @app_util.Cog.command(
            command=app_util.MessageCommand(name='Pin'),
            guild_id=877399405056102431
        )
        async def pin(self, ctx: app_util.Context, message: discord.Message):
            await message.pin()
            await ctx.send_response(f'Message pinned by {ctx.author}', ephemeral=True)

        @app_util.Cog.command(
            command=app_util.SlashCommand(
                name='modal',
                description='sends a placeholder modal',
            ),
            guild_id=1234567890
        )
        async def modal_command(self, ctx: app_util.Context, name: str):
            # creating a modal with author's name
            modal = app_util.Modal(client=self.bot, title=f'A Super Modal for {ctx.author.name}')
            modal.add_field(
                label='About',
                custom_id='about',
                style=app_util.TextInputStyle.PARAGRAPH,
                required=False,
                hint='Write something about yourself...',
            )
            modal.add_field(
                label='Tip',
                custom_id='tip',
                style=app_util.TextInputStyle.SHORT,
                required=True,
                hint='Give me some tips to improve...',
                max_length=100,
            )
            await ctx.send_modal(modal)  # sending the modal

            @modal.callback  # in-place callback for the modal
            async def on_submit(mcx: app_util.Context, about: str, tip: str):
                embed = discord.Embed(
                    description=f'**About:** {about}\n**Tip:** {tip}')
                embed.set_author(name=f'{mcx.author.name}', icon_url=mcx.author.avatar.url)
                await mcx.send_response(embed=embed)

        # error handler
        @app_util.Cog.listener
        async def on_command_error(self, ctx: app_util.Context, error: Exception):
            stack = traceback.format_exception(type(error), error, error.__traceback__)
            await ctx.send_followup(f'```py\n{"".join(stack)}\n```')


    def setup(bot: app_util.Bot):
        bot.add_application_cog(Sample(bot))


