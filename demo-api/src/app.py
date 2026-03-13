import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src import items, logging_config

logging_config.configure()
logger = logging.getLogger(__name__)

app = FastAPI()


class SimulatedFailureError(Exception):
    pass


@app.exception_handler(SimulatedFailureError)
async def simulated_failure_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


class ItemIn(BaseModel):
    name: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/items")
def list_items():
    logger.info("Listing all items")
    return items.get_all()


@app.post("/items", status_code=201)
def create_item(body: ItemIn):
    return items.create(body.name)


@app.get("/items/fail")
def fail():
    logger.error("Simulated failure triggered")
    raise SimulatedFailureError("Intentional failure endpoint — demo-api v2 error simulation")


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = items.get_one(item_id)
    if item is None:
        logger.warning("Item not found id=%d", item_id)
        raise HTTPException(status_code=404, detail="not found")
    return item
