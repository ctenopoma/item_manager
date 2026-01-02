from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from . import models, database
from .routers import auth, users, items
from sqladmin import Admin
from .admin import UserAdmin, ItemAdmin, LogAdmin, NotificationSettingsAdmin, EmailTemplateAdmin
import asyncio
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from .notification import check_and_send_notifications
from .database import SessionLocal

models.Base.metadata.create_all(bind=database.engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Background task loop
    async def notification_loop():
        print("Notification scheduler started.")
        while True:
            now = datetime.now()
            # Target: Today 8:00 AM
            target = now.replace(hour=8, minute=0, second=0, microsecond=0)
            
            # If 8:00 AM has already passed today, target tomorrow 8:00 AM
            if now >= target:
                target += timedelta(days=1)
            
            seconds_to_wait = (target - now).total_seconds()
            print(f"Next notification check at {target} (in {seconds_to_wait:.0f} seconds)")
            
            await asyncio.sleep(seconds_to_wait)

            try:
                print("Running daily notification check...")
                db = SessionLocal()
                check_and_send_notifications(db)
                db.close()
            except Exception as e:
                print(f"Error in notification loop: {e}")

    task = asyncio.create_task(notification_loop())
    yield
    task.cancel()

app = FastAPI(title="Equipment Management System", lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

app.mount("/static", StaticFiles(directory="inventory_app/static"), name="static")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)

admin = Admin(app, database.engine)
admin.add_view(UserAdmin)
admin.add_view(ItemAdmin)
admin.add_view(LogAdmin)
admin.add_view(NotificationSettingsAdmin)
admin.add_view(EmailTemplateAdmin)
