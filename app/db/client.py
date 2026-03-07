from fastapi import Request, HTTPException
import httpx

from app.db.schema import Author, AuthorCreate, AuthorAndDiary


class Client:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10)

    async def close(self):
        await self.client.aclose()

    async def get_author(self, author_id: int) -> Author:
        response = await self._get(f"/authors/{author_id}")
        return Author(**response.json())

    async def get_all_authors(self) -> list[Author]:
        response = await self._get("/authors/")
        return [Author(**author) for author in response.json()]

    async def create_author(self, author: AuthorCreate) -> AuthorAndDiary:
        response = await self._post("/authors/", json=author.model_dump(mode="json"))
        return AuthorAndDiary(**response.json())

    async def get_author_filters(self):
        response = await self._get("/authors/filters")
        return response.json()

    # TODO: add for notes
    # TODO: add for points

    async def _request(self, *args, **kwargs) -> httpx.Response:
        response = await self.client.request(*args, **kwargs)
        return response.raise_for_status()

    async def _get(self, *args, **kwargs) -> httpx.Response:
        return await self._request("GET", *args, **kwargs)

    async def _post(self, *args, **kwargs) -> httpx.Response:
        return await self._request("POST", *args, **kwargs)


async def get_db_client(request: Request):
    return request.app.state.db_client
