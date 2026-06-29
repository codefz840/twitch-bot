import os

__all__ = (
    "TWITCH_CLIENT_ID",
    "TWITCH_CLIENT_SECRET",
    "BOT_ID",
    "OWNER_ID",
    "OSUIRC_USER",
    "OSUIRC_PASS",
    "OSU_USER",
    "OSU_PASS",
)

TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")
BOT_ID = os.environ.get("BOT_ID")
OWNER_ID = os.environ.get("OWNER_ID")
OSUIRC_USER = os.environ.get("OSUIRC_USER")
OSUIRC_PASS = os.environ.get("OSUIRC_PASS")
