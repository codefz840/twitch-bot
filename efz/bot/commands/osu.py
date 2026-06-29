import logging
import twitchio
from twitchio.ext import commands
from urllib.parse import urlparse
from typing import TYPE_CHECKING

from efz import env

if TYPE_CHECKING:
    from efz.bot import Bot840

LOGGER = logging.getLogger("twitch-bot")


def is_beatmap_url(url: str) -> bool:
    try:
        parsed_url = urlparse(url.strip())
        if parsed_url.netloc != "osu.ppy.sh":
            return False

        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 2:
            return False

        if path_parts[0] in ["b", "s", "beatmapsets", "beatmaps"]:
            return True

        return False
    except Exception as e:
        return False


class OsuCommand(commands.Component):
    def __init__(self, bot: "Bot840"):
        self.bot = bot

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage):
        if payload.broadcaster.id != env.OWNER_ID:
            return

        if is_beatmap_url(payload.text):
            await self.bot.osuirc.send("840", f"來自 {payload.chatter.name} 的 osu! 連結: {payload.text}")

async def setup(bot: "Bot840"):
    await bot.add_component(OsuCommand(bot))