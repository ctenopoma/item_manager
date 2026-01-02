from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from . import models, database
from .routers import auth, users, items
from sqladmin import Admin
from .admin import UserAdmin, ItemAdmin, LogAdmin

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Equipment Management System")

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
