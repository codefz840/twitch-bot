from fastapi.responses import Response, RedirectResponse
from contextlib import asynccontextmanager
from .fastapiadapter import FastAPIAdapter

@asynccontextmanager
async def lifespan(app: FastAPIAdapter):
    await app.event_startup()
    yield
    await app.event_shutdown()

app = FastAPIAdapter(lifespan=lifespan)