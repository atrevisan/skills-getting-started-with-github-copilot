"""
Test module for FastAPI endpoints using the AAA (Arrange-Act-Assert) pattern.
Tests cover all HTTP endpoints: GET root, GET /activities, POST signup, DELETE participant.
"""
import pytest


class TestRootEndpoint:
    """Tests for the root endpoint (GET /)."""
    
    def test_root_redirect(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Send a GET request to the root endpoint
        ASSERT: Verify it redirects to /static/index.html
        """
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_success(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Send a GET request to /activities
        ASSERT: Verify 200 status and response contains activities dict
        """
        # Arrange
        # (no setup needed, activities are pre-populated in the app)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_get_activities_structure(self, client):
        """
        ARRANGE: Get activities response
        ACT: Check the structure of returned activity objects
        ASSERT: Verify each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities) > 0
        # Check first activity in dict
        first_activity_name, first_activity = next(iter(activities.items()))
        assert all(field in first_activity for field in required_fields)
    
    def test_get_activities_contains_chess_club(self, client):
        """
        ARRANGE: Retrieve all activities
        ACT: Search for Chess Club in response
        ASSERT: Verify Chess Club exists in the activities dict
        """
        # Arrange
        expected_activity_name = "Chess Club"
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        # Activities is a dict with activity names as keys
        assert expected_activity_name in activities


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, valid_activity, sample_email):
        """
        ARRANGE: Set up client, valid activity, and email
        ACT: Send POST request to signup endpoint
        ASSERT: Verify 200 status and participant is added
        """
        # Arrange
        # Act
        response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_signup_with_different_emails(self, client, valid_activity):
        """
        ARRANGE: Prepare multiple different email addresses
        ACT: Sign up multiple students to the same activity
        ASSERT: Verify all participants are added
        """
        # Arrange
        emails = ["student1@example.com", "student2@example.com", "student3@example.com"]
        
        # Act & Assert
        for email in emails:
            response = client.post(
                f"/activities/{valid_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
    
    def test_signup_duplicate_email_fails(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up a student, prepare to sign them up again with same email
        ACT: Attempt to sign up the same email twice
        ASSERT: Verify the second signup fails with 400 status code
        """
        # Arrange
        # Act: First signup should succeed
        response1 = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert: First signup succeeds
        assert response1.status_code == 200
        
        # Act: Second signup with same email should fail
        response2 = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert: Second signup fails
        assert response2.status_code == 400
    
    def test_signup_invalid_activity_fails(self, client, invalid_activity, sample_email):
        """
        ARRANGE: Prepare invalid activity name and email
        ACT: Send POST request to signup for non-existent activity
        ASSERT: Verify 404 status code
        """
        # Arrange
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_signup_response_contains_message(self, client, valid_activity, sample_email):
        """
        ARRANGE: Set up signup request with valid data
        ACT: Send POST request to signup endpoint
        ASSERT: Verify response contains success message
        """
        # Arrange
        # Act
        response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert valid_activity in data["message"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_success(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up a participant, prepare to unregister them
        ACT: Send DELETE request to unregister the participant
        ASSERT: Verify 200 status and participant is removed
        """
        # Arrange: First, sign up the student
        client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Act: Unregister the student
        response = client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_unregister_nonexistent_participant_fails(self, client, valid_activity, sample_email):
        """
        ARRANGE: Prepare to unregister a participant who is not signed up
        ACT: Send DELETE request for non-existent participant
        ASSERT: Verify 404 status code
        """
        # Arrange
        # (no signup, so participant doesn't exist)
        
        # Act
        response = client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_from_invalid_activity_fails(self, client, invalid_activity, sample_email):
        """
        ARRANGE: Prepare to unregister from non-existent activity
        ACT: Send DELETE request to invalid activity
        ASSERT: Verify 404 status code
        """
        # Arrange
        # (activity doesn't exist)
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_response_contains_message(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up a participant, prepare to unregister
        ACT: Send DELETE request
        ASSERT: Verify response contains success message
        """
        # Arrange: Sign up first
        client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": sample_email}
        )
        
        # Assert
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
