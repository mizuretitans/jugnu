import logging

from fastapi import FastAPI

from app.routers import auth, bookings, chats, dashboard, mentors, mentorship

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="Jugnu API", docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None)

for module in (auth, mentors, mentorship, bookings, chats, dashboard):
    app.include_router(module.router, prefix="/api")
