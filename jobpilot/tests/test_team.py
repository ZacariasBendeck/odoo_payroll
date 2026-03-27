def test_create_member(client):
    resp = client.post(
        "/api/team",
        json={"name": "Alice", "email": "alice@example.com", "role": "Developer", "skills": "Python, FastAPI"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Alice"
    assert data["role"] == "Developer"


def test_list_members(client):
    client.post("/api/team", json={"name": "Alice"})
    client.post("/api/team", json={"name": "Bob"})

    resp = client.get("/api/team")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_assign_task(client):
    project = client.post("/api/projects", json={"name": "P1"}).json()
    task = client.post(
        "/api/tasks", json={"project_id": project["id"], "title": "Task 1"}
    ).json()
    member = client.post("/api/team", json={"name": "Alice"}).json()

    resp = client.post(
        f"/api/tasks/{task['id']}/assign",
        json={"member_id": member["id"], "notes": "Please handle this"},
    )
    assert resp.status_code == 201
    assert resp.json()["member_name"] == "Alice"


def test_member_workload(client):
    project = client.post("/api/projects", json={"name": "P1"}).json()
    task = client.post(
        "/api/tasks", json={"project_id": project["id"], "title": "Task 1"}
    ).json()
    member = client.post("/api/team", json={"name": "Bob"}).json()
    client.post(f"/api/tasks/{task['id']}/assign", json={"member_id": member["id"]})

    resp = client.get(f"/api/team/{member['id']}/workload")
    assert resp.status_code == 200
    assert resp.json()["active_assignments"] == 1
