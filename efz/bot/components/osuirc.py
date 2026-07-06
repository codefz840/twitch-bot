import asyncio
from twitchio.ext import commands
from osuirc import IrcClient as OsuIrcClient
from efz.bot import Bot840
from efz import env
from efz.utils.logger import component

log = component("osuirc")

async def setup(bot: "Bot840"):
    if env.OSUIRC_USER is None or env.OSUIRC_PASS is None:
        log.warning("Osu IRC 無帳號或密碼，不啟動")        
        return
    
    if hasattr(bot, "osuirc"):
        await bot.osuirc.stop()
        del bot.osuirc

    log.info("正在啟動 OsuIRC 組件...")
    bot.osuirc = OsuIrcClient(env.OSUIRC_USER, env.OSUIRC_PASS)
    asyncio.create_task(bot.osuirc.run())
