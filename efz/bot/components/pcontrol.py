from twitchio import eventsub
from twitchio.ext import commands
import twitchio
from efz.bot import Bot840
from efz.utils.logger import component
from efz import env
from wayland_automation.keyboard_controller import Keyboard
import json
import subprocess


log = component("pcontrol")


class PCControl(commands.Component):
    def __init__(self, bot: "Bot840"):
        self.bot = bot

    def get_niri_focused_window(self):
        try:
            # 執行 niri msg --json focused-window
            # text=True 讓輸出直接是字串，capture_output=True 用來捕捉 stdout/stderr
            result = subprocess.run(
                ["niri", "msg", "--json", "focused-window"],
                capture_output=True,
                text=True,
                check=True,  # 如果指令執行失敗（例如非 niri 環境），會直接拋出異常
            )

            # 將標準輸出（JSON 字串）解析為 Python 字典
            return json.loads(result.stdout)

        except subprocess.CalledProcessError as e:
            log.error(f"執行 niri 指令失敗: {e.stderr}")
            return None
        except FileNotFoundError:
            log.error("系統中找不到 niri 指令，請確認是否已安裝並加入 PATH。")
            return None
    
    @commands.reward_command(id='c6c195b3-2d03-4be9-8e01-02732b23d208')
    async def switch_random_skin(self, ctx: commands.Context):
        focused_window = self.get_niri_focused_window()
        if focused_window is None:
            return  # 如果無法取得焦點視窗，直接返回
        if focused_window.get("app_id") in ["osu!.exe", "osu!"]:
            subprocess.run(["xdotool", "key", "ctrl+shift+r"])
            
        

async def setup(bot: "Bot840"):
    """Must have channel:read:redemptions or channel:manage:redemptions scope."""
    await bot.add_component(PCControl(bot))
    await bot.multi_subscribe([eventsub.ChannelPointsRedeemAddSubscription(
        broadcaster_user_id=env.OWNER_ID, reward_id="c6c195b3-2d03-4be9-8e01-02732b23d208")])