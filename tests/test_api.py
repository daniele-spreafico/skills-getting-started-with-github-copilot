import sys
import pathlib
import urllib.parse

from fastapi.testclient import TestClient


# Ensure src is importable
HERE = pathlib.Path(__file__).parent.resolve()
SRC = str(HERE.parent / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import app as app_module

client = TestClient(app_module.app)


def quote(name: str) -> str:
    return urllib.parse.quote(name, safe="")


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Clean up if already present
    res = client.get("/activities")
    assert res.status_code == 200
    participants = res.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{quote(activity)}/unregister?email={urllib.parse.quote(email)}")

    # Sign up
    res = client.post(f"/activities/{quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")

    # Verify present
    res = client.get("/activities")
    assert email in res.json()[activity]["participants"]

    # Unregister
    res = client.delete(f"/activities/{quote(activity)}/unregister?email={urllib.parse.quote(email)}")
    assert res.status_code == 200
    assert "Unregistered" in res.json().get("message", "")

    # Verify removed
    res = client.get("/activities")
    assert email not in res.json()[activity]["participants"]


def test_unregister_nonexistent():
    res = client.delete("/activities/Chess%20Club/unregister?email=nonexistent@example.com")
    assert res.status_code == 404
