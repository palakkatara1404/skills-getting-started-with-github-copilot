import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def restore_activities():
    initial_state = copy.deepcopy(activities)

    yield

    activities.clear()
    activities.update(initial_state)


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_all_default_activities(self, client, restore_activities):
        # Arrange
        expected_activity_names = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Club",
            "Music Ensemble",
            "Robotics Club",
            "Debate Team",
        }

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == expected_activity_names

        for activity in data.values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_success(self, client, restore_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        before_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == before_count + 1

    def test_duplicate_signup_is_rejected(self, client, restore_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        before_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert len(activities[activity_name]["participants"]) == before_count

    def test_signup_for_missing_activity_returns_404(self, client, restore_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_multiple_signups_for_same_activity_work(self, client, restore_activities):
        # Arrange
        activity_name = "Programming Class"
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        before_count = len(activities[activity_name]["participants"])

        # Act
        for index, email in enumerate(emails):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email},
            )

            # Assert
            assert response.status_code == 200
            assert response.json()["message"] == f"Signed up {email} for {activity_name}"
            assert len(activities[activity_name]["participants"]) == before_count + index + 1
            assert email in activities[activity_name]["participants"]
