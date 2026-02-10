"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.get("/my-activities")
def get_my_activities(email: str):
    """Get all activities a student is registered for"""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    my_activities = {}
    for activity_name, details in activities.items():
        if email in details["participants"]:
            my_activities[activity_name] = details
    
    return my_activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate email is provided
    if not email or email.strip() == "":
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student isn't already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")
    
    # Check if activity is at capacity
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")
        
    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants/{email}")
def remove_participant(activity_name: str, email: str):
    """Remove a participant from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate participant is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Remove participant
    activity["participants"].remove(email)
    return {"message": f"Removed {email} from {activity_name}"}
