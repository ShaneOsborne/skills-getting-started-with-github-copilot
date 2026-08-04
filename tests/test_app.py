from src import app as app_module


def test_root_redirects_to_static_app(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    chess_club = response.json()["Chess Club"]
    assert set(chess_club) == {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }
    assert chess_club["max_participants"] == 12
    assert chess_club["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert app_module.activities["Chess Club"]["participants"].count(email) == 1


def test_signup_rejects_duplicate_participant(client):
    email = "michael@mergington.edu"
    participants_before = list(app_module.activities["Chess Club"]["participants"])

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert app_module.activities["Chess Club"]["participants"] == participants_before


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client):
    response = client.post("/activities/Chess%20Club/signup")

    assert response.status_code == 422


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_rejects_unknown_participant(client):
    participants_before = list(app_module.activities["Chess Club"]["participants"])

    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "unknown@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Participant not found in this activity"
    }
    assert app_module.activities["Chess Club"]["participants"] == participants_before


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_requires_email(client):
    response = client.delete("/activities/Chess%20Club/participants")

    assert response.status_code == 422


def test_activity_state_starts_from_seed_data(client):
    participants = client.get("/activities").json()["Chess Club"]["participants"]

    assert participants == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]