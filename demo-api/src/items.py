import logging

logger = logging.getLogger(__name__)

_store: dict[int, dict] = {}
_next_id = 1


def get_all() -> list[dict]:
    return list(_store.values())


def get_one(item_id: int) -> dict | None:
    return _store.get(item_id)


def create(name: str) -> dict:
    global _next_id
    item = {"id": _next_id, "name": name}
    _store[_next_id] = item
    logger.info("Created item id=%d name=%s", _next_id, name)
    _next_id += 1
    return item
