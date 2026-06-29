from sqlmodel import Session, select, and_
import twitchio
from twitchio.ext import commands
from efz.utils.logger import log
from efz.db.database import engine
from efz.db.models import CustomCommand as MCustomCommand
import random
import time

class CustomCommand(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def setup(self):
        with Session(engine) as db:
            stmt = select(MCustomCommand)
            custom_commands = db.exec(stmt).all()
            for cmd in custom_commands:
                self.build_command(cmd.name)

    @commands.command()
    async def testcmd(self, ctx: commands.Context, params: str):
        if ctx.author.id != self.bot.owner_id:
            return
    
        globalspace = {
            "__builtins__": None
        }
        localspace = {
            "sender": ctx.author,
            "channel": ctx.channel,
            "params": params
        }
        test = params.strip()
        result = eval(test, globalspace, localspace)
        await ctx.send(str(result)[:500])  # 限制回應長度避免過長


    def build_command(self, name):
        if name in self.bot.commands:
            return
        new_command = commands.Command(name=name, callback=self.exec_custom_command)
        self.bot.add_command(new_command)


    async def exec_custom_command(self, ctx: commands.Context, *params):
        cmd = ctx.command.name
        with Session(engine) as db:
            stmt = select(MCustomCommand).where(and_(MCustomCommand.channel == ctx.channel.id, MCustomCommand.name == cmd))
            command = db.exec(stmt).one_or_none()
        if not command:
            return
        return await self.custom_command(command, ctx, *params)


    async def custom_command(self, command: MCustomCommand, ctx: commands.Context, *params):
        _random = random.Random(time.time())
        globalspace = {
            "__builtins__": None
        }
        localspace = {
            "sender": ctx.author,
            "channel": ctx.channel,
            "params": params,
            "random": _random.randint,
            "choice": _random.choice,

        }
        
        result = eval(command.response, globalspace, localspace)
        response = str(result)
        if len(response) > 500:
            response = response[:497] + "..."
        await ctx.reply(response)


    @commands.command()
    async def addcmd(self, ctx: commands.Context, name: str, response: str):
        name = name.strip().lower()
        response = response.strip()
        with Session(engine) as db:
            command = db.exec(select(MCustomCommand).where(and_(MCustomCommand.channel == ctx.channel.id, MCustomCommand.name == name))).one_or_none()
            if command:
                return await ctx.reply("指令已存在")
    
            custom_command = MCustomCommand(
                channel=ctx.channel.id,
                name=name,
                response=response
            )
            db.add(custom_command)
            db.commit()
        self.build_command(name)
        await ctx.reply(f"已新增 '{name}' 指令")


    @commands.command()
    async def modcmd(self, ctx: commands.Context, name: str, response: str):
        name = name.strip().lower()
        response = response.strip()
        with Session(engine) as db:
            stmt = select(MCustomCommand).where(and_(MCustomCommand.channel == ctx.channel.id, MCustomCommand.name == name))
            custom_command = db.exec(stmt).one_or_none()
            if not custom_command:
                return await ctx.reply("找不到指令")
            custom_command.response = response
            db.add(custom_command)
            db.commit()

        await ctx.send(f"已更新 '{name}' 指令")


    @commands.command()
    async def rmcmd(self, ctx: commands.Context, name: str):
        name = name.strip().lower()
        with Session(engine) as db:
            stmt = select(MCustomCommand).where(and_(MCustomCommand.channel == ctx.channel.id, MCustomCommand.name == name))
            custom_command = db.exec(stmt).one_or_none()
            if not custom_command:
                return await ctx.reply("找不到指令")
            db.delete(custom_command)
            db.commit()
        await ctx.reply(f"已刪除 '{name}' 指令") 


async def setup(bot: commands.Bot):
    component = CustomCommand(bot)
    await bot.add_component(component)
    await component.setup()