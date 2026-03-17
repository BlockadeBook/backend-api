from fastapi import APIRouter, Depends

from app.api.author.schema import Author, AuthorCreate, AuthorAndDiary
from app.db.client import Client, get_db_client

router = APIRouter(prefix="/author")


@router.get("/", response_model=list[Author])
async def get_all_authors(db_client: Client = Depends(get_db_client)):
    return await db_client.get_all_authors()


@router.get("/filters")
async def get_author_filters(db_client: Client = Depends(get_db_client)):
    return await db_client.get_author_filters()


@router.get("/{author_id}", response_model=Author)
async def get_author(author_id: int, db_client: Client = Depends(get_db_client)):
    return await db_client.get_author(author_id)


@router.post("/", response_model=AuthorAndDiary)
async def create_author(author: AuthorCreate, db_client: Client = Depends(get_db_client)):
    return await db_client.create_author(author)
