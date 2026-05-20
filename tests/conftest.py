import pytest
from fastapi.testclient import TestClient
from src import app as app_module


@pytest.fixture
def client():
    """
    Provides a TestClient instance for making requests to the FastAPI application.
    Creates a fresh app instance for each test to ensure test isolation.
    """
    # Reset the activities dict to its initial state before each test
    app_module.activities.clear()
    app_module.activities.update({
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
            "description": "Competitive basketball practice and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Yoga Club": {
            "description": "Mindful stretching and strength-building exercises",
            "schedule": "Wednesdays, 5:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media art",
            "schedule": "Mondays and Thursdays, 3:45 PM - 5:15 PM",
            "max_participants": 16,
            "participants": ["lily@mergington.edu", "sam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, stagecraft, and put on school performances",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["chloe@mergington.edu", "ryan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Build public speaking skills and compete in debates",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["nina@mergington.edu", "derek@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Work on science challenges and prepare for competitions",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["sarah@mergington.edu", "kevin@mergington.edu"]
        }
    })
    return TestClient(app_module.app)


@pytest.fixture
def sample_email():
    """Provides a sample email for testing."""
    return "student@example.com"


@pytest.fixture
def valid_activity():
    """Provides a valid activity name from the app's activities."""
    return "Chess Club"


@pytest.fixture
def invalid_activity():
    """Provides an invalid activity name."""
    return "NonexistentActivity"
