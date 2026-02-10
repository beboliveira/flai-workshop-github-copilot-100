"""
Test suite for Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the API"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities database before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis lessons and tournament preparation",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["jessica@mergington.edu", "ryan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, theater production, and stage performance",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["maya@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["zoe@mergington.edu", "ethan@mergington.edu"]
        },
        "Robotics Workshop": {
            "description": "Build and program robots with cutting-edge technology",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 5,
            "participants": ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu", "diana@mergington.edu"]
        }
    }
    
    # Reset to original state before each test
    activities.clear()
    activities.update(original_activities)
    yield


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test successful retrieval of all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 10  # Updated to include Robotics Workshop
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Robotics Workshop" in data
    
    def test_get_activities_structure(self, client):
        """Test that each activity has correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)
            assert isinstance(details["max_participants"], int)
    
    def test_get_activities_chess_club_details(self, client):
        """Test Chess Club has correct initial data"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration(self, client):
        """Test that duplicate registration is prevented"""
        email = "michael@mergington.edu"  # Already registered for Chess Club
        
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up"
    
    def test_signup_multiple_activities(self, client):
        """Test student can sign up for multiple different activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Drama Club
        response2 = client.post(f"/activities/Drama Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Drama Club"]["participants"]
    
    def test_signup_with_url_encoding(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post("/activities/Programming%20Class/signup?email=coder@mergington.edu")
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "coder@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestMyActivitiesEndpoint:
    """Test the GET /my-activities endpoint"""
    
    def test_get_my_activities_with_registrations(self, client):
        """Test getting activities for a student with registrations"""
        email = "michael@mergington.edu"  # Already registered for Chess Club
        
        response = client.get(f"/my-activities?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert email in data["Chess Club"]["participants"]
    
    def test_get_my_activities_empty(self, client):
        """Test getting activities for a student with no registrations"""
        email = "noactivities@mergington.edu"
        
        response = client.get(f"/my-activities?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 0
    
    def test_get_my_activities_multiple(self, client):
        """Test getting multiple activities for one student"""
        email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        client.post(f"/activities/Chess Club/signup?email={email}")
        client.post(f"/activities/Drama Club/signup?email={email}")
        client.post(f"/activities/Science Club/signup?email={email}")
        
        response = client.get(f"/my-activities?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Drama Club" in data
        assert "Science Club" in data
    
    def test_get_my_activities_no_email(self, client):
        """Test getting activities without providing email"""
        response = client.get("/my-activities")
        assert response.status_code == 422  # Validation error
    
    def test_get_my_activities_after_removal(self, client):
        """Test getting activities after being removed from one"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Remove from Chess Club
        client.delete(f"/activities/Chess Club/participants/{email}")
        
        response = client.get(f"/my-activities?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "Chess Club" not in data


class TestRemoveParticipantEndpoint:
    """Test the DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self, client):
        """Test successful removal of a participant"""
        email = "michael@mergington.edu"
        
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_remove_participant_activity_not_found(self, client):
        """Test removing participant from non-existent activity returns 404"""
        response = client.delete("/activities/NonExistent/participants/test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_remove_participant_not_found(self, client):
        """Test removing non-existent participant returns 404"""
        response = client.delete("/activities/Chess Club/participants/notregistered@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Participant not found"
    
    def test_remove_participant_preserves_others(self, client):
        """Test removing one participant doesn't affect others"""
        # Chess Club has michael and daniel
        response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")
        assert response.status_code == 200
        
        # Verify daniel is still there
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        chess_participants = activities_data["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in chess_participants
        assert "daniel@mergington.edu" in chess_participants
    
    def test_remove_and_re_signup(self, client):
        """Test that a removed participant can sign up again"""
        email = "michael@mergington.edu"
        
        # Remove participant
        remove_response = client.delete(f"/activities/Chess Club/participants/{email}")
        assert remove_response.status_code == 200
        
        # Sign up again
        signup_response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify they're back
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_signup_workflow(self, client):
        """Test complete workflow: check activities, sign up, verify, remove"""
        email = "workflow@mergington.edu"
        activity = "Science Club"
        
        # Check initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify added
        after_signup = client.get("/activities")
        after_signup_data = after_signup.json()
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        assert email in after_signup_data[activity]["participants"]
        
        # Remove
        remove_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert remove_response.status_code == 200
        
        # Verify removed
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert len(final_data[activity]["participants"]) == initial_count
        assert email not in final_data[activity]["participants"]


class TestCapacityLimits:
    """Test activity capacity and full status"""
    
    def test_robotics_workshop_near_capacity(self, client):
        """Test Robotics Workshop with only 1 spot left"""
        response = client.get("/activities")
        data = response.json()
        
        robotics = data["Robotics Workshop"]
        assert robotics["max_participants"] == 5
        assert len(robotics["participants"]) == 4
        # One spot left
        assert robotics["max_participants"] - len(robotics["participants"]) == 1
    
    def test_signup_fills_last_spot(self, client):
        """Test signing up for the last available spot"""
        email = "laststudent@mergington.edu"
        
        # Sign up for last spot in Robotics Workshop
        response = client.post(f"/activities/Robotics Workshop/signup?email={email}")
        assert response.status_code == 200
        
        # Verify activity is now full
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        robotics = activities_data["Robotics Workshop"]
        assert len(robotics["participants"]) == robotics["max_participants"]
        assert email in robotics["participants"]
    
    def test_signup_when_activity_full(self, client):
        """Test that signup fails when activity is at capacity"""
        # Fill the last spot
        response1 = client.post("/activities/Robotics Workshop/signup?email=laststudent@mergington.edu")
        assert response1.status_code == 200
        
        # Verify activity is now full
        activities_data = client.get("/activities").json()
        robotics = activities_data["Robotics Workshop"]
        assert len(robotics["participants"]) == robotics["max_participants"]
        
        # Try to sign up when full - should fail
        response2 = client.post("/activities/Robotics Workshop/signup?email=toolate@mergington.edu")
        assert response2.status_code == 400
        assert "full" in response2.json()["detail"].lower()
        
        # Verify participant was not added
        activities_data = client.get("/activities").json()
        robotics = activities_data["Robotics Workshop"]
        assert "toolate@mergington.edu" not in robotics["participants"]
        assert len(robotics["participants"]) == robotics["max_participants"]
    
    def test_capacity_tracking_across_operations(self, client):
        """Test that capacity is correctly tracked through signup and removal"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Fill last spot
        client.post(f"/activities/Robotics Workshop/signup?email={email1}")
        
        # Verify full
        response = client.get("/activities")
        data = response.json()
        assert len(data["Robotics Workshop"]["participants"]) == 5
        
        # Remove one participant
        client.delete(f"/activities/Robotics Workshop/participants/{email1}")
        
        # Verify spot opened
        response = client.get("/activities")
        data = response.json()
        assert len(data["Robotics Workshop"]["participants"]) == 4
        
        # Someone else can now sign up
        response = client.post(f"/activities/Robotics Workshop/signup?email={email2}")
        assert response.status_code == 200


class TestMyActivitiesAdvanced:
    """Advanced tests for /my-activities endpoint"""
    
    def test_my_activities_with_full_activity(self, client):
        """Test my-activities shows activities even when full"""
        email = "alice@mergington.edu"  # Already in Robotics Workshop
        
        response = client.get(f"/my-activities?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "Robotics Workshop" in data
        assert email in data["Robotics Workshop"]["participants"]
    
    def test_my_activities_after_signup_and_removal_cycle(self, client):
        """Test my-activities correctly updates through signup and removal"""
        email = "cycletest@mergington.edu"
        
        # Initially no activities
        response = client.get(f"/my-activities?email={email}")
        assert len(response.json()) == 0
        
        # Sign up for multiple activities
        client.post(f"/activities/Chess Club/signup?email={email}")
        client.post(f"/activities/Drama Club/signup?email={email}")
        
        # Should show 2 activities
        response = client.get(f"/my-activities?email={email}")
        data = response.json()
        assert len(data) == 2
        assert "Chess Club" in data
        assert "Drama Club" in data
        
        # Remove from one
        client.delete(f"/activities/Chess Club/participants/{email}")
        
        # Should show only 1 activity
        response = client.get(f"/my-activities?email={email}")
        data = response.json()
        assert len(data) == 1
        assert "Drama Club" in data
        assert "Chess Club" not in data
    
    def test_my_activities_special_characters_in_email(self, client):
        """Test my-activities with special characters in email"""
        email = "student+test@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Check my activities
        response = client.get(f"/my-activities?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
    
    def test_my_activities_with_all_activities(self, client):
        """Test student registered for all activities"""
        email = "superactive@mergington.edu"
        
        # Get all activities
        all_activities = client.get("/activities").json()
        
        # Sign up for all non-full activities
        for activity_name, details in all_activities.items():
            if len(details["participants"]) < details["max_participants"]:
                client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Check my activities
        response = client.get(f"/my-activities?email={email}")
        data = response.json()
        
        # Should have signed up for multiple activities
        assert len(data) >= 5
        
        # All returned activities should have the email
        for activity_name, details in data.items():
            assert email in details["participants"]


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_signup_with_empty_email(self, client):
        """Test signup with empty email parameter"""
        response = client.post("/activities/Chess Club/signup?email=")
        # Should either return 400 or 422 for validation error
        assert response.status_code in [400, 422]
    
    def test_remove_participant_twice(self, client):
        """Test removing the same participant twice"""
        email = "michael@mergington.edu"
        
        # Remove once
        response1 = client.delete(f"/activities/Chess Club/participants/{email}")
        assert response1.status_code == 200
        
        # Try to remove again
        response2 = client.delete(f"/activities/Chess Club/participants/{email}")
        assert response2.status_code == 404
    
    def test_activity_name_case_sensitivity(self, client):
        """Test that activity names are case-sensitive"""
        response = client.post("/activities/chess club/signup?email=test@mergington.edu")
        assert response.status_code == 404
    
    def test_concurrent_signups_different_activities(self, client):
        """Test signing up for different activities in sequence"""
        email = "concurrent@mergington.edu"
        
        # Sign up for multiple activities
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        response2 = client.post(f"/activities/Drama Club/signup?email={email}")
        response3 = client.post(f"/activities/Tennis Club/signup?email={email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # Verify all signups
        activities_data = client.get("/activities").json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Drama Club"]["participants"]
        assert email in activities_data["Tennis Club"]["participants"]
    
    def test_all_activities_count(self, client):
        """Test that all 10 activities are loaded"""
        response = client.get("/activities")
        data = response.json()
        
        # Should have 10 activities including Robotics Workshop
        assert len(data) == 10
        assert "Robotics Workshop" in data
        assert "Chess Club" in data
        assert "Science Club" in data
    
    def test_participant_preservation_after_failed_signup(self, client):
        """Test that participants list is not modified after failed signup"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Get initial participants
        initial_data = client.get("/activities").json()
        initial_participants = initial_data["Chess Club"]["participants"].copy()
        
        # Try duplicate signup (should fail)
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400
        
        # Verify participants list unchanged
        final_data = client.get("/activities").json()
        final_participants = final_data["Chess Club"]["participants"]
        assert final_participants == initial_participants


class TestIntegrationWorkflows:
    """Additional integration tests for complex workflows"""
    
    def test_student_journey_full_cycle(self, client):
        """Test a complete student journey through the system"""
        email = "newstudent@mergington.edu"
        
        # 1. Check available activities
        all_activities = client.get("/activities").json()
        assert len(all_activities) > 0
        
        # 2. Student has no activities initially
        my_activities = client.get(f"/my-activities?email={email}").json()
        assert len(my_activities) == 0
        
        # 3. Sign up for Chess Club
        signup = client.post(f"/activities/Chess Club/signup?email={email}")
        assert signup.status_code == 200
        
        # 4. Verify in my activities
        my_activities = client.get(f"/my-activities?email={email}").json()
        assert len(my_activities) == 1
        assert "Chess Club" in my_activities
        
        # 5. Sign up for another activity
        client.post(f"/activities/Drama Club/signup?email={email}")
        
        # 6. Should have 2 activities
        my_activities = client.get(f"/my-activities?email={email}").json()
        assert len(my_activities) == 2
        
        # 7. Remove from one activity
        client.delete(f"/activities/Chess Club/participants/{email}")
        
        # 8. Should have 1 activity left
        my_activities = client.get(f"/my-activities?email={email}").json()
        assert len(my_activities) == 1
        assert "Drama Club" in my_activities
        assert "Chess Club" not in my_activities
    
    def test_activity_fills_and_empties(self, client):
        """Test filling an activity to capacity and then emptying it"""
        # Fill Robotics Workshop (has 4 participants, max 5)
        client.post("/activities/Robotics Workshop/signup?email=fill1@mergington.edu")
        
        # Verify full
        data = client.get("/activities").json()
        assert len(data["Robotics Workshop"]["participants"]) == 5
        
        # Remove all participants
        participants = data["Robotics Workshop"]["participants"].copy()
        for email in participants:
            client.delete(f"/activities/Robotics Workshop/participants/{email}")
        
        # Verify empty
        data = client.get("/activities").json()
        assert len(data["Robotics Workshop"]["participants"]) == 0
        
        # Can sign up again
        response = client.post("/activities/Robotics Workshop/signup?email=newperson@mergington.edu")
        assert response.status_code == 200

