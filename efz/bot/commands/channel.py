from twitchio.ext import commands


class ChannelCommand(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # @commands.command()
    # async def title(self, ctx: commands.Context, *, title: str):
    #     await ctx.reply(f"Title set to: {title}")

    # @commands.command()
    # async def game(self, ctx: commands.Context, *, game: str):
    #     await ctx.reply(f"Game set to: {game}")


async def setup(bot: commands.Bot):
    await bot.add_component(ChannelCommand(bot))