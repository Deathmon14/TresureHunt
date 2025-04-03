import json
import os
import datetime

# File to store team data
TEAM_DATA_FILE = "team_data.json"

# Load team data from file or initialize if file doesn't exist
if os.path.exists(TEAM_DATA_FILE):
    with open(TEAM_DATA_FILE, "r") as file:
        team_data = json.load(file)
else:
    team_data = {
        "team_progress": {}, 
        "team_scores": {}, 
        "team_streaks": {},
        "team_routes": {},
        "team_timers": {},
        "team_powerups": {},
        "team_bonus_challenges": {},
        "leaderboard": []
    }

# Expose team data variables
team_progress = team_data.get("team_progress", {})
team_scores = team_data.get("team_scores", {})
team_streaks = team_data.get("team_streaks", {})
team_routes = team_data.get("team_routes", {})
team_timers = team_data.get("team_timers", {})
team_powerups = team_data.get("team_powerups", {})
team_bonus_challenges = team_data.get("team_bonus_challenges", {})
leaderboard = team_data.get("leaderboard", [])

# Convert string timestamps back to datetime objects
for team_id, timer_data in team_timers.items():
    if "start_time" in timer_data and isinstance(timer_data["start_time"], str):
        try:
            timer_data["start_time"] = datetime.datetime.fromisoformat(timer_data["start_time"])
        except ValueError:
            # If conversion fails, set to current time
            timer_data["start_time"] = datetime.datetime.now()

# Function to save team data to file
def save_team_data():
    # Convert datetime objects to strings for JSON serialization
    serializable_timers = {}
    for team_id, timer_data in team_timers.items():
        serializable_timers[team_id] = {
            "start_time": timer_data["start_time"].isoformat() if "start_time" in timer_data else None
        }
    
    # Create a fresh leaderboard
    updated_leaderboard = []
    for team_id, score_data in team_scores.items():
        if team_id in team_routes:
            updated_leaderboard.append({
                "team_id": team_id,
                "score": score_data["score"],
                "route": team_routes[team_id],
                "progress": team_progress.get(team_id, 1)
            })
    
    # Sort leaderboard by score (highest first)
    updated_leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    with open(TEAM_DATA_FILE, "w") as file:
        json.dump({
            "team_progress": team_progress, 
            "team_scores": team_scores, 
            "team_streaks": team_streaks,
            "team_routes": team_routes,
            "team_timers": serializable_timers,
            "team_powerups": team_powerups,
            "team_bonus_challenges": team_bonus_challenges,
            "leaderboard": updated_leaderboard
        }, file)