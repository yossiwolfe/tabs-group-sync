import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .main import app, get_db
from .models import Base

TEST_DB_URL = "sqlite:///:memory:" # we're running a new DB in memory so as not to mess with our actual DB

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool # this is to avoid two threads disconnecting simultaneously and causing memory issues
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear() # clear the dependency override after the test completes


def test_health_check(client):
    """ Test that the health check works """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}

def test_empty_groups(client):
    """ Test that no groups exist when none are created """
    response = client.get("/groups")
    assert response.status_code == 200
    assert response.json() == []

def test_create_tab_group(client):
    """ Test that a tab group can be created """

    payload = {
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Tab Group 1",
        "color": "3D3D3D",
        "device_id": "iphone12-1",
    }

    response = client.post("/groups", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == payload["user_id"]
    assert data["name"] == payload["name"]
    assert data["color"] == payload["color"]
    assert data["device_id"] == payload["device_id"]
    assert "id" in data
    assert data["deleted"] == False

def test_create_tab_group_fails_when_color_prop_past_max_length(client):
    """ Test that a tab group fails to be created when color max length is not respected """

    payload = {
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Tab Group 1",
        "color": "ffffffffffeeeeeeeeeerrrrrrrrrruuuuuuuuuuoooooooooollllllllll",
        "device_id": "iphone12-1",
    }

    response = client.post("/groups", json=payload)

    assert response.status_code == 422

def test_create_tab_group_fails_when_device_id_prop_past_max_length(client):
    """ Test that a tab group fails to be created when device_id max length is not respected """

    payload = {
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Tab Group 1",
        "color": "3d3d3d",
        "device_id": "ffffffffffeeeeeeeeeerrrrrrrrrruuuuuuuuuuoooooooooollllllllllffffffffffeeeeeeeeeerrrrrrrrrruuuuuuuuuuoooooooooollllllllllffffffffffeeeeeeeeeerrrrrrrrrruuuuuuuuuuoooooooooollllllllllffffffffffeeeeeeeeeerrrrrrrrrruuuuuuuuuuoooooooooollllllllllffffffffffeeeeeeeeeerrrrrrrrrruuuuuuuuuuoooooooooollllllllllffffffffffeeeeeeeeeerrrrrrrrrruuuuuuuuuuoooooooooollllllllllffffffffffeeeeeeeeeerrrrrrrrrruuuuuuuuuuoooooooooollllllllll",
    }

    response = client.post("/groups", json=payload)

    assert response.status_code == 422

def test_create_one_hundred_tab_groups(client):
    """ Test that 1000 tab groups can be created """

    tabGroupsToCreate = 1000

    payload = {
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Tab Group 1",
        "color": "3D3D3D",
        "device_id": "iphone12-1",
    }

    for i in range(tabGroupsToCreate):
        payload["name"] = f"Tab Group {i}"
        response = client.post("/groups", json=payload)
        assert response.status_code == 201

    response = client.get("/groups")
    assert response.status_code == 200
    assert len(response.json()) == tabGroupsToCreate

def test_update_tab_group(client):
    """ Test that a tab group can be updated """

    createPayload = {
            "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "Tab Group 1",
            "color": "3D3D3D",
            "device_id": "iphone12-1",
        }
    
    createResponse = client.post("/groups", json=createPayload)
    id = createResponse.json()["id"]

    updatePayload = {
        "name": "Best Tab Group Ever",
    }

    response = client.patch(f"/groups/{id}", json=updatePayload)

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == createPayload["user_id"]
    assert data["name"] == updatePayload["name"]
    assert data["color"] == createPayload["color"]
    assert data["device_id"] == createPayload["device_id"]
    assert "id" in data
    assert data["deleted"] == False

def test_delete_tab_group(client):
    """ Test that a tab group can be soft deleted """

    createPayload = {
            "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "Tab Group 1",
            "color": "3D3D3D",
            "device_id": "iphone12-1",
        }
    
    createResponse = client.post("/groups", json=createPayload)
    id = createResponse.json()["id"]

    response = client.delete(f"/groups/{id}")

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == createPayload["user_id"]
    assert data["name"] == createPayload["name"]
    assert data["color"] == createPayload["color"]
    assert data["device_id"] == createPayload["device_id"]
    assert "id" in data
    assert data["deleted"] == True

def test_deleted_tab_groups_only_show_with_since(client):
    """ Test that a tab groups get returns deleted tab groups only when since is used """

    createPayload = {
            "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "Tab Group 1",
            "color": "3D3D3D",
            "device_id": "iphone12-1",
        }
    
    createResponse = client.post("/groups", json=createPayload)
    createResponseData = createResponse.json()
    id = createResponseData["id"]

    client.delete(f"/groups/{id}")

    getResponseWithoutSince = client.get("/groups")
    dataWithoutSince = getResponseWithoutSince.json()

    assert len(dataWithoutSince) == 0

    getResponseWithSince = client.get("/groups", params={"since": createResponseData["updated_at"]})
    dataWithSince = getResponseWithSince.json()

    assert len(dataWithSince) == 1

