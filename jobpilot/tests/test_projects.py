def test_create_project(client):
    resp = client.post(
        "/api/projects",
        json={"name": "Test Project", "description": "A test project", "priority": "high"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Project"
    assert data["priority"] == "high"
    assert data["status"] == "planning"


def test_list_projects(client):
    client.post("/api/projects", json={"name": "Project 1"})
    client.post("/api/projects", json={"name": "Project 2"})

    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_project(client):
    create = client.post("/api/projects", json={"name": "My Project"})
    pid = create.json()["id"]

    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "My Project"


def test_update_project(client):
    create = client.post("/api/projects", json={"name": "Old Name"})
    pid = create.json()["id"]

    resp = client.put(f"/api/projects/{pid}", json={"name": "New Name", "status": "active"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"
    assert resp.json()["status"] == "active"


def test_delete_project(client):
    create = client.post("/api/projects", json={"name": "To Delete"})
    pid = create.json()["id"]

    resp = client.delete(f"/api/projects/{pid}")
    assert resp.status_code == 204

    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 404


def test_create_task(client):
    project = client.post("/api/projects", json={"name": "Task Project"}).json()

    resp = client.post(
        "/api/tasks",
        json={"project_id": project["id"], "title": "Fix bug", "priority": "high"},
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Fix bug"


def test_create_goal(client):
    project = client.post("/api/projects", json={"name": "Goal Project"}).json()

    resp = client.post(
        f"/api/projects/{project['id']}/goals",
        json={"title": "Launch MVP", "status": "not_started"},
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Launch MVP"
