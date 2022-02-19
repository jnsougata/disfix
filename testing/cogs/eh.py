import sys
import asyncio
import traceback
import discord
import src.extslash as extslash



class Error(extslash.Cog):

    def __init__(self, bot: extslash.Bot):
        self.bot = bot

    @extslash.Cog.listener
    async def on_command_error(self, ctx: extslash.ApplicationContext, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await ctx.send_followup(f'```py\n{tb}\n```')

    @extslash.Cog.command(
        command=extslash.SlashCommand(
            name='all',
            description='get all commands',
            options=[
                extslash.IntOption(
                    name='page',
                    description='page number',
                    max_value=10,
                    min_value=1,
                    required=True,
                )
            ]
        ),
        guild_id=877399405056102431
    )
    async def all_command(self, ctx: extslash.ApplicationContext):
        await ctx.defer()
        await self.bot.sync_global_commands()
        print(ctx.command.default_access)
        await ctx.send_followup(f'```py\n{self.bot.application_commands}\n```')




def setup(bot: extslash.Bot):
    bot.add_slash_cog(Error(bot))
