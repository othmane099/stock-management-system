import pytest
from httpx import AsyncClient, ASGITransport
from starlette.testclient import TestClient

from src.sms.adapters.entry_points.api.app import app
from src.sms.core.domain.dtos import CreateBrandDTO, UpdateBrandDTO

client = TestClient(app)


@pytest.mark.asyncio(loop_scope="session")
async def test_create(drop_and_create_database):
    dto = CreateBrandDTO(name="e2e_brand_name", description="e2e_brand_description")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1") as ac:
        response = await ac.post(
            "/api/v1/brands",
            json=CreateBrandDTO.model_dump(dto)
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] is not None
        assert response.json()["data"]["name"] == dto.name
        assert response.json()["data"]["description"] == dto.description
        assert response.json()["data"]["created_at"] is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_update(get_brand_service_impl):
    brands = await get_brand_service_impl.find_all(page=1, size=10)
    existed_brand = brands.items[0]
    dto = UpdateBrandDTO(id=existed_brand.id, name="updated_e2e_brand_name", description=existed_brand.description)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1") as ac:
        response = await ac.put(
            "/api/v1/brands",
            json=UpdateBrandDTO.model_dump(dto)
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == dto.id
        assert response.json()["data"]["name"] == dto.name
        assert response.json()["data"]["description"] == dto.description
        assert response.json()["data"]["created_at"] is not None
        assert response.json()["data"]["updated_at"] is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_brands(get_brand_service_impl):
    brands = await get_brand_service_impl.find_all(page=1, size=10)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1") as ac:
        response = await ac.get(
            "/api/v1/brands?page=1&size=10"
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) == len(brands.items)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_brand(get_brand_service_impl):
    brand = await get_brand_service_impl.find_by_id(1)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1") as ac:
        response = await ac.get(
            "/api/v1/brands/1"
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == brand.id
        assert response.json()["data"]["name"] == brand.name
        assert response.json()["data"]["description"] == brand.description
        assert response.json()["data"]["created_at"] == brand.created_at


@pytest.mark.asyncio(loop_scope="session")
async def test_delete(get_brand_service_impl):
    existed_brand_before_delete = await get_brand_service_impl.find_all(page=1, size=10)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1") as ac:
        response = await ac.delete(
            "/api/v1/brands/1"
        )
        assert response.status_code == 200
        assert response.json()["detail"] == "Brand deleted successfully"

    existed_brand_after_delete = await get_brand_service_impl.find_all(page=1, size=10)
    assert  len(existed_brand_after_delete.items) == len(existed_brand_before_delete.items) - 1