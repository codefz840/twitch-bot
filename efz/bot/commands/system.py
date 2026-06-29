import time

from twitchio.ext import commands


class SystemCommand(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def botuptime(self, ctx: commands.Context):
        uptime = time.time() - self.bot.startup_time
        await ctx.reply(f"Bot 已運行 {uptime} 秒！")


async def setup(bot: commands.Bot):
    await bot.add_component(SystemCommand(bot))