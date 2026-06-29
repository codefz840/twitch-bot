import asyncio

from sqlmodel import Session, select
from twitchio import eventsub

from efz.bot import Bot840
from efz.db.database import engine, setup_database
from efz.db.models import Token
import efz.env as env
from efz.utils.logger import log
from osuirc import IrcClient as OsuIrcClient

async def setup_token_and_subscriptions():
    """從資料庫初始化 Token 與 Twitch 訂閱事件"""
    tokens: list[tuple[str, str]] = []
    subs: list[eventsub.SubscriptionPayload] = []

    with Session(engine) as session:
        statement = select(Token)
        db_tokens = session.exec(statement).all()

        for token in db_tokens:
            tokens.append((token.token, token.refresh))

            # 略過機器人自身的訂閱
            if token.user_id == env.BOT_ID:
                continue

            chat_sub = eventsub.ChatMessageSubscription(
                broadcaster_user_id=token.user_id, 
                user_id=env.BOT_ID
            )
            subs.append(chat_sub)

    return tokens, subs

async def main():
    setup_database()
    
    tokens, subs = await setup_token_and_subscriptions()

    async with Bot840(subs=subs) as bot:
        # 批量加入 Token
        for token_pair in tokens:
            await bot.add_token(*token_pair)
        
        await bot.start(load_tokens=False),


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("程序已被使用者手動中止。")