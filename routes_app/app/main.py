# routes_app/app/main.py
# Final edit by PilarM
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .api import router as api_router

app = FastAPI(title="routes_app")
app.include_router(api_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.get("/ping")
def ping():
    return {"status": "pong"}
