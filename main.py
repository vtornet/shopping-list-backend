from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import databases
import sqlalchemy
import os
import time
import uuid

# ==============================
# DATABASE CONFIG (Railway)
# ==============================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost/postgres"
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# ==============================
# TABLES
# ==============================

lists = sqlalchemy.Table(
    "lists",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True, autoincrement=True),
    sqlalchemy.Column("server_id", sqlalchemy.String, unique=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("owner_id", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("members_emails", sqlalchemy.ARRAY(sqlalchemy.String)),
    sqlalchemy.Column("created_at", sqlalchemy.BigInteger),
    sqlalchemy.Column("updated_at", sqlalchemy.BigInteger),
)

items = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True, autoincrement=True),
    sqlalchemy.Column("server_id", sqlalchemy.String, unique=True),
    sqlalchemy.Column("list_server_id", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("in_shopping_list", sqlalchemy.Boolean),
    sqlalchemy.Column("quantity", sqlalchemy.Integer),
    sqlalchemy.Column("image_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("price", sqlalchemy.Float, nullable=True),
    sqlalchemy.Column("previous_price", sqlalchemy.Float, nullable=True),
    sqlalchemy.Column("added_by_uid", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.BigInteger),
    sqlalchemy.Column("updated_at", sqlalchemy.BigInteger),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

# ==============================
# FASTAPI APP
# ==============================

app = FastAPI(title="Shopping List API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Pydantic Models
# ==============================

class ListCreate(BaseModel):
    name: str
    owner_id: str
    members_emails: List[str] = []

class ItemCreate(BaseModel):
    list_server_id: str
    name: str
    in_shopping_list: bool = True
    quantity: int = 1
    image_url: Optional[str] = None
    price: Optional[float] = None
    previous_price: Optional[float] = None
    added_by_uid: Optional[str] = None

# ==============================
# LIST ENDPOINTS
# ==============================

@app.get("/lists")
async def get_lists(user_id: Optional[str] = None):
    query = sqlalchemy.select(lists)
    if user_id:
        query = query.where(lists.c.owner_id == user_id)
    return await database.fetch_all(query)

@app.post("/lists")
async def create_list(lst: ListCreate):
    now = int(time.time() * 1000)
    server_id = str(uuid.uuid4())

    query = lists.insert().values(
        server_id=server_id,
        name=lst.name,
        owner_id=lst.owner_id,
        members_emails=lst.members_emails,
        created_at=now,
        updated_at=now,
    )

    record_id = await database.execute(query)

    return {
        "id": record_id,
        "server_id": server_id,
        "name": lst.name,
        "owner_id": lst.owner_id,
        "members_emails": lst.members_emails,
        "created_at": now,
        "updated_at": now,
    }

@app.put("/lists/{list_id}")
async def update_list(list_id: int, lst: ListCreate):
    now = int(time.time() * 1000)

    query = (
        sqlalchemy.update(lists)
        .where(lists.c.id == list_id)
        .values(
            name=lst.name,
            members_emails=lst.members_emails,
            updated_at=now,
        )
    )

    await database.execute(query)
    return {"status": "ok"}

@app.delete("/lists/{list_id}")
async def delete_list(list_id: int):
    query = sqlalchemy.delete(lists).where(lists.c.id == list_id)
    await database.execute(query)
    return {"status": "ok"}

# ==============================
# ITEM ENDPOINTS
# ==============================

@app.get("/items")
async def get_items(list_server_id: Optional[str] = None):
    query = sqlalchemy.select(items)
    if list_server_id:
        query = query.where(items.c.list_server_id == list_server_id)
    return await database.fetch_all(query)

@app.post("/items")
async def create_item(item: ItemCreate):
    now = int(time.time() * 1000)
    server_id = str(uuid.uuid4())

    query = items.insert().values(
        server_id=server_id,
        list_server_id=item.list_server_id,
        name=item.name,
        in_shopping_list=item.in_shopping_list,
        quantity=item.quantity,
        image_url=item.image_url,
        price=item.price,
        previous_price=item.previous_price,
        added_by_uid=item.added_by_uid,
        created_at=now,
        updated_at=now,
    )

    record_id = await database.execute(query)

    return {
        "id": record_id,
        "server_id": server_id,
        "name": item.name,
        "list_server_id": item.list_server_id,
        "in_shopping_list": item.in_shopping_list,
        "quantity": item.quantity,
        "image_url": item.image_url,
        "price": item.price,
        "previous_price": item.previous_price,
        "added_by_uid": item.added_by_uid,
        "created_at": now,
        "updated_at": now,
    }

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: ItemCreate):
    now = int(time.time() * 1000)

    query = (
        sqlalchemy.update(items)
        .where(items.c.id == item_id)
        .values(
            name=item.name,
            in_shopping_list=item.in_shopping_list,
            quantity=item.quantity,
            image_url=item.image_url,
            price=item.price,
            previous_price=item.previous_price,
            updated_at=now,
        )
    )

    await database.execute(query)
    return {"status": "ok"}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    query = sqlalchemy.delete(items).where(items.c.id == item_id)
    await database.execute(query)
    return {"status": "ok"}

# ==============================
# HEALTH CHECK
# ==============================

@app.get("/")
async def root():
    return {"status": "ok", "message": "Shopping List API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
