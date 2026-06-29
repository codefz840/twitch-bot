import itertools
from pathlib import Path
from sqlmodel import Session, select
from twitchio.ext.commands import AutoBot
from twitchio import eventsub
import twitchio
import time
from typing import TYPE_CHECKING
from efz.db.database import engine
from efz.db.models import Token
from efz.utils.logger import log
from efz.web import app as adapter
import efz.env as env

if TYPE_CHECKING:
    from osuirc import IrcClient as OsuIrcClient
    from efz.bot.components.tosu import Tosu



class Bot840(AutoBot):
    osuirc: "OsuIrcClient"
    tosu: "Tosu"

    def __init__(self, *, subs: list[eventsub.SubscriptionPayload]):
        self.startup_time = time.time()
        super().__init__(
            client_id=env.TWITCH_CLIENT_ID,
            client_secret=env.TWITCH_CLIENT_SECRET,
            bot_id=env.BOT_ID,
            owner_id=env.OWNER_ID,
            prefix="!",
            subscriptions=subs,
            force_subscribe=True,
            adapter=adapter
        )

    async def setup_hook(self) -> None:
        paths = itertools.chain(
            Path("efz/bot/commands").glob("*.py"),
            Path("efz/bot/components").glob("*.py")
        )
        for file in paths:
            module_name = f"{str(file.parent).replace("/", ".")}.{file.stem}"
            await self.load_module(module_name)
            log.debug("模組 %s 載入完成", file.stem)


    async def event_oauth_authorized(
        self, payload: twitchio.authentication.UserTokenPayload
    ) -> None:
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        if payload.user_id == self.bot_id:
            # We usually don't want subscribe to events on the bots channel...
            return

        # A list of subscriptions we would like to make to the newly authorized channel...
        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(
                broadcaster_user_id=payload.user_id, user_id=self.bot_id
            ),
        ]

        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            log.warning("無法訂閱：%r，使用者：%s", resp.errors, payload.user_id)

    async def add_token(
        self, token: str, refresh: str
    ) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(
            token, refresh
        )

        new_token = Token(user_id=resp.user_id, token=token, refresh=refresh)
        with Session(engine) as session:
            exist_token = session.exec(
                select(Token).where(Token.user_id == resp.user_id)
            ).one_or_none()
            if exist_token:
                exist_token.token = token
                exist_token.refresh = refresh
                session.add(exist_token)
            else:
                session.add(new_token)
            session.commit()

        log.info("已將令牌添加到資料庫，使用者：%s", resp.user_id)
        return resp

    async def event_ready(self) -> None:
        log.info("成功登入，使用者：%s", self.bot_id)
