
import asyncio
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from twitchio.ext import commands
from efz.utils.logger import log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver

class ComponentReloadHandler(FileSystemEventHandler):
    """監聽組件目錄變更並動態熱加載的事件處理器"""

    def __init__(self, bot: commands.Bot, loop: asyncio.AbstractEventLoop):
        self.bot = bot
        self.loop = loop  # 儲存主線程的 Event Loop

    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return
        file = Path(event.src_path)
        module_name = f"{str(file.parent).replace("/", ".")}.{Path(event.src_path).stem}"
        log.debug("偵測到 %s 更新，嘗試重新加載模組", module_name)
        
        try:
            # 修正：Watchdog 運作在獨立執行緒，必須使用 run_coroutine_threadsafe 送回主執行緒執行
            future = asyncio.run_coroutine_threadsafe(
                self.bot.reload_module(module_name), self.loop
            )
            future.result()  # 等待執行結果，若協程出錯會在這裡拋出異常
            log.info("模組 %s 熱加載成功!", module_name)
        except Exception as e:
            log.error("模組 %s 熱加載失敗: %s", module_name, e)


observer_instance: BaseObserver = None

async def setup(bot: commands.Bot):
    global observer_task, observer_instance

    if observer_instance:
        observer_instance.stop()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, observer_instance.join)

    observer_instance = Observer()
    current_loop = asyncio.get_running_loop()
    event_handler = ComponentReloadHandler(bot, current_loop)
    observer_instance.schedule(event_handler, path="efz/bot/commands", recursive=False)
    observer_instance.schedule(event_handler, path="efz/bot/components", recursive=False)
    observer_instance.start()
    log.debug("WatchDog 已啟動")