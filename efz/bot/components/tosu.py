import asyncio
import json
import websockets
from typing import Any
from twitchio.ext import commands
from efz.bot.bot import Bot840

class Tosu(commands.Component):
    def __init__(self, bot: Bot840):
        self.bot = bot
        self.ws = websockets.connect("ws://localhost:24050/ws")
        self._data = None
        self.running = False
        self.task = None
        self.bot.tosu = self

    async def start(self):
        self.running = True
        self.task = asyncio.create_task(self.runner())

    async def stop(self):
        self.running = False
        self.task.cancel()
        self.task = None

    async def runner(self):
        async with self.ws as ws:
            while self.running:
                try:
                    message = await ws.recv()
                    await self.parse(message)
                except:
                    pass

    async def parse(self, data: str):
        self._data = json.loads(data)
    
    @property
    def data(self) -> Any:
        return self._data
    
    @staticmethod
    def _get_deep(data: Any, path: str) -> Any:
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict):
                if key not in current:
                    return "undefined"
                current = current[key]
            else:
                if not hasattr(current, key):
                    return "undefined"
                current = getattr(current, key)
        if current is None:
            return "None"
        return str(current)

    @commands.command()
    async def tosu(self, ctx: commands.Context, attribute: str):
        if not self.running:
            await ctx.reply("Tosu 組件未啟動")
            return
        data = self.data
        if data is None:
            await ctx.reply("undefined")
            return
        value = self._get_deep(data, attribute)
        if len(value) > 500:
            value = value[:497] + "..."
        await ctx.reply(value)

async def setup(bot: "Bot840"):
    if hasattr(bot, "tosu"):
        await bot.tosu.stop()
        del bot.tosu

    await bot.add_component(Tosu(bot))
    asyncio.create_task(bot.tosu.start())
