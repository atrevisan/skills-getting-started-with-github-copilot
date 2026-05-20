"""
Test module for business logic validation using the AAA (Arrange-Act-Assert) pattern.
Tests cover validation, data integrity, and business rule enforcement.
"""
import pytest


class TestSignupValidation:
    """Tests for signup business logic and validation."""
    
    def test_signup_email_persists_after_signup(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up a student
        ACT: Retrieve activities list
        ASSERT: Verify email appears in the activity's participants
        """
        # Arrange
        # Act: Sign up
        response_signup = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        assert response_signup.status_code == 200
        
        # Act: Retrieve activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Find the activity and verify email is in participants
        activity_dict = activities[valid_activity]
        assert sample_email in activity_dict["participants"]
    
    def test_multiple_signups_same_activity(self, client, valid_activity):
        """
        ARRANGE: Prepare multiple emails
        ACT: Sign up all to same activity
        ASSERT: Verify all are present in activity participants
        """
        # Arrange
        emails = [
            "alice@example.com",
            "bob@example.com",
            "charlie@example.com"
        ]
        
        # Act: Sign up all students
        for email in emails:
            client.post(
                f"/activities/{valid_activity}/signup",
                params={"email": email}
            )
        
        # Assert: Verify all are in the activity
        response = client.get("/activities")
        activities = response.json()
        activity_data = activities[valid_activity]
        
        for email in emails:
            assert email in activity_data["participants"]
    
    def test_signup_returns_success_message(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up a student
        ACT: Retrieve the signup response
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


class TestUnregisterValidation:
    """Tests for unregister business logic and validation."""
    
    def test_unregister_email_removed_from_activity(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up and then unregister a student
        ACT: Retrieve activities list
        ASSERT: Verify email no longer appears in participants
        """
        # Arrange: Sign up
        client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Act: Unregister
        client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": sample_email}
        )
        
        # Act: Retrieve activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        activity_data = activities[valid_activity]
        assert sample_email not in activity_data["participants"]
    
    def test_signup_unregister_signup_again(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up, unregister, then attempt to sign up again
        ACT: Perform all three actions in sequence
        ASSERT: Verify can sign up again after unregistering
        """
        # Arrange
        # Act & Assert: First signup succeeds
        response1 = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Act & Assert: Unregister succeeds
        response2 = client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": sample_email}
        )
        assert response2.status_code == 200
        
        # Act & Assert: Can sign up again
        response3 = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        assert response3.status_code == 200
        assert "message" in response3.json()


class TestDataIntegrity:
    """Tests for data structure and integrity."""
    
    def test_activity_structure_consistency(self, client):
        """
        ARRANGE: Retrieve activities
        ACT: Check structure of each activity
        ASSERT: Verify all activities have consistent structure
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Activities is a dict with activity names as keys
        assert isinstance(activities, dict)
        for activity_name, activity_data in activities.items():
            assert all(field in activity_data for field in required_fields)
            assert isinstance(activity_name, str)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert all(isinstance(p, str) for p in activity_data["participants"])
    
    def test_participants_is_list_of_strings(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up a participant
        ACT: Get the activity response
        ASSERT: Verify participants is a list of strings
        """
        # Arrange
        # Act
        response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert: Response has a message
        data = response.json()
        assert "message" in data
        
        # Verify by getting activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        activity_data = activities[valid_activity]
        assert isinstance(activity_data["participants"], list)
        assert all(isinstance(p, str) for p in activity_data["participants"])
    
    def test_max_participants_field_exists(self, client):
        """
        ARRANGE: Retrieve activities
        ACT: Check max_participants field
        ASSERT: Verify max_participants is an integer
        """
        # Arrange & Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestActivitiesExist:
    """Tests to verify expected activities are in the system."""
    
    def test_default_activities_exist(self, client):
        """
        ARRANGE: Get all activities
        ACT: Check for specific pre-populated activities
        ASSERT: Verify expected activities exist
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Yoga Club"
        ]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        activity_names = list(activities.keys())
        
        # Assert
        for activity in expected_activities:
            assert activity in activity_names
