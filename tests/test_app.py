from __future__ import annotations

import uuid

import pytest
from fake.repository import FakeRepository
from fastapi.testclient import TestClient
from ferrea.clients.db import ConnectionSettings, Neo4jClient
from ferrea.core.context import Context

from app import app as spinup_app
from models.repository import RepositoryService
from routers._builder import build_repository

PREFIX = "/api/v1/libraries"


@pytest.fixture
def client() -> TestClient:
    def mock_repository_dependency() -> RepositoryService:
        context = Context(uuid=str(uuid.uuid4()), app="LBS_TST")
        conn_sett = ConnectionSettings(
            uri="",
            user="",
            password="",
        )
        return FakeRepository(context=context, db_client=Neo4jClient(conn_sett))

    app = spinup_app()
    app.dependency_overrides[build_repository] = mock_repository_dependency
    return TestClient(app)


def test_no_libraries(client: TestClient) -> None:
    """Test with an empty repository."""
    response = client.get(PREFIX)

    expected = {"result": [], "items": 0}
    actual = response.json()

    assert response.status_code == 200
    assert actual == expected
