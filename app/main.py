from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .config import Settings
from .routers import tasks
from .routers import ai as ai_router
# put a small icon at app/static/favicon.ico
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse



settings = Settings()
app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("app/static/favicon.ico")

@app.get("/", include_in_schema=False)
def root():
    # Theory: keep your API stateless and point humans to the docs UI
    return RedirectResponse(url="/docs")

@app.get("/health",tags=["infra"])
def health():
    return {"status":"ok"}

#routes

app.include_router(tasks.router)
app.include_router(ai_router.router)