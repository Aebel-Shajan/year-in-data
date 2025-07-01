from fastapi import FastAPI
from app.api.routes import tables

app = FastAPI(title="Year in data backend")
app.include_router(tables.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)