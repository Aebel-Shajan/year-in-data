import time
from fastapi import FastAPI, Request
from app.api.routes import tables
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

app = FastAPI(title="Year in data backend")
app.include_router(tables.router)

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # in milliseconds
    formatted_process_time = f"{process_time:.2f}ms"

    logger.info(f"{request.method} {request.url.path} completed in {formatted_process_time}")

    # You can also add the timing info to the response headers (optional)
    response.headers["X-Process-Time"] = formatted_process_time
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)