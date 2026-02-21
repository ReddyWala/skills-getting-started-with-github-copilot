import urllib.parse

from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def test_get_activities():
    # Arrange: no setup required

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_duplicate_and_delete_flow():
    # Arrange
    activity = "Chess Club"
    encoded = urllib.parse.quote(activity, safe="")
    email = "test_user@example.com"
    participants = app_module.activities[activity]["participants"]
    # ensure test starts from a clean state
    if email in participants:
        participants.remove(email)

    # Act: sign up the user
    resp = client.post(f"/activities/{encoded}/signup", params={"email": email})

    # Assert: signup succeeded and participant present
    assert resp.status_code == 200, resp.text
    assert email in app_module.activities[activity]["participants"]

    # Act: attempt duplicate signup
    resp_dup = client.post(f"/activities/{encoded}/signup", params={"email": email})

    # Assert: duplicate rejected
    assert resp_dup.status_code == 400

    # Act: remove the participant
    resp_del = client.delete(f"/activities/{encoded}/participants", params={"email": email})

    # Assert: deletion succeeded and participant removed
    assert resp_del.status_code == 200, resp_del.text
    assert email not in app_module.activities[activity]["participants"]

    # Act: try deleting again
    resp_del2 = client.delete(f"/activities/{encoded}/participants", params={"email": email})

    # Assert: second deletion fails
    assert resp_del2.status_code == 400
