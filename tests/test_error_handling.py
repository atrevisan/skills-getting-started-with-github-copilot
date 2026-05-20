"""
Test module for error handling using the AAA (Arrange-Act-Assert) pattern.
Tests cover HTTP error responses, validation failures, and edge cases.
"""
import pytest


class TestSignupErrorHandling:
    """Tests for signup endpoint error handling."""
    
    def test_signup_invalid_activity_returns_404(self, client, sample_email):
        """
        ARRANGE: Prepare invalid activity name
        ACT: Attempt to sign up for invalid activity
        ASSERT: Verify 404 status code is returned
        """
        # Arrange
        invalid_activity = "NonexistentActivity"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_signup_duplicate_email_returns_400(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up a student once
        ACT: Attempt to sign up same email again
        ASSERT: Verify 400 status code is returned
        """
        # Arrange
        client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Act
        response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 400
    
    def test_signup_duplicate_error_message_clear(self, client, valid_activity, sample_email):
        """
        ARRANGE: Sign up a student
        ACT: Attempt duplicate signup and check error response
        ASSERT: Verify error message indicates duplicate signup
        """
        # Arrange
        client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Act
        response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_signup_activity_not_found_error_message(self, client, sample_email):
        """
        ARRANGE: Prepare request for non-existent activity
        ACT: Send signup request to invalid activity
        ASSERT: Verify error message indicates activity not found
        """
        # Arrange
        invalid_activity = "NonexistentActivity"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()


class TestUnregisterErrorHandling:
    """Tests for unregister endpoint error handling."""
    
    def test_unregister_invalid_activity_returns_404(self, client, sample_email):
        """
        ARRANGE: Prepare invalid activity name
        ACT: Attempt to unregister from invalid activity
        ASSERT: Verify 404 status code is returned
        """
        # Arrange
        invalid_activity = "NonexistentActivity"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_nonexistent_participant_returns_404(self, client, valid_activity, sample_email):
        """
        ARRANGE: Prepare valid activity but participant not signed up
        ACT: Attempt to unregister participant who is not signed up
        ASSERT: Verify 404 status code is returned
        """
        # Arrange
        # Act
        response = client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_nonexistent_participant_error_message(self, client, valid_activity, sample_email):
        """
        ARRANGE: Prepare request to unregister non-existent participant
        ACT: Send DELETE request
        ASSERT: Verify error message indicates participant not found
        """
        # Arrange
        # Act
        response = client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_signup_with_existing_participants(self, client, valid_activity, sample_email):
        """
        ARRANGE: Retrieve activity with existing participants
        ACT: Sign up a new participant
        ASSERT: Verify participant is added correctly
        """
        # Arrange
        # Act: Sign up new participant
        response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify by getting the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        activity_data = activities[valid_activity]
        assert sample_email in activity_data["participants"]
    
    def test_signup_multiple_activities_isolated(self, client, sample_email):
        """
        ARRANGE: Get two different activities
        ACT: Sign up same email to both activities
        ASSERT: Verify email appears in both but no cross-contamination
        """
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Yoga Club"
        
        # Act: Sign up to first activity
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": sample_email}
        )
        
        # Act: Sign up to second activity
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": sample_email}
        )
        
        # Assert: Both signups succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Assert: Verify email in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert sample_email in activities[activity1]["participants"]
        assert sample_email in activities[activity2]["participants"]
    
    def test_case_sensitive_activity_names(self, client, sample_email):
        """
        ARRANGE: Prepare activity name with different case
        ACT: Attempt signup with wrong case
        ASSERT: Verify case-sensitive matching (should fail)
        """
        # Arrange
        wrong_case_activity = "chess club"
        
        # Act: Try with wrong case
        response = client.post(
            f"/activities/{wrong_case_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert: Should fail (case-sensitive)
        assert response.status_code == 404
    
    def test_signup_different_emails_duplicate_blocked(self, client, valid_activity):
        """
        ARRANGE: Prepare multiple different emails
        ACT: Sign up each to same activity (should all succeed)
        ASSERT: Verify all participants are present, no duplicates allowed
        """
        # Arrange
        emails = ["email1@test.com", "email2@test.com", "email3@test.com"]
        
        # Act & Assert: All different emails should succeed
        for email in emails:
            response = client.post(
                f"/activities/{valid_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert: Duplicate of same email should fail
        duplicate_response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": emails[0]}
        )
        assert duplicate_response.status_code == 400
