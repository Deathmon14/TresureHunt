from fastapi import FastAPI, HTTPException, Header, Request
from config import settings
from middleware import security_middleware, get_rate_limiter
from clues1 import clues, bonus_challenges
from team_data import (
    team_progress, team_scores, team_streaks, team_routes,
    team_timers, team_powerups, team_bonus_challenges, save_team_data
)
import random
import datetime
import logging
import os
from fastapi.staticfiles import StaticFiles
from difflib import SequenceMatcher
from fastapi import Request

from utils import generate_bonus_challenge, generate_congrats_message, verify_answer_hybrid

app = FastAPI(middleware=security_middleware)
limiter = get_rate_limiter()
app.state.limiter = limiter
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

''' def verify_answer_static(correct_answer: str, team_answer: str) -> bool:
    """Static verification without LLM"""
    return team_answer.lower().strip() == correct_answer.lower().strip()'''

def verify_answer_static(correct_answer: str, team_answer: str) -> bool:
    correct = correct_answer.lower().strip()
    attempt = team_answer.lower().strip()
    similarity = SequenceMatcher(None, correct, attempt).ratio()
    return similarity > 0.85  # 85% match is usually safe

def generate_hint_static(answer: str) -> str:
    """Generate a simple hint without LLM"""
    return f"🔍 HINT: The answer starts with '{answer[0]}' and has {len(answer)} letters."

@app.post("/register_team")
@limiter.limit("10/minute")
async def register_team(request: Request, data: dict):
    try:
        team_id = data.get("team_id", "").strip()
        team_name = data.get("team_name", f"Team {team_id}").strip()
        
        if len(team_id) < 3:
            raise HTTPException(status_code=400, detail="Team ID must be at least 3 characters")
            
        if team_id in team_routes:
            route = team_routes[team_id]
            clue_id = team_progress.get(team_id, 1)
            return {
                "response": f"Team {team_name} already registered on route {route.upper()}. Continue with your current clue.",
                "route": route,
                "clue": clues[route][clue_id]["question"] if clue_id in clues[route] else "Completed all clues!"
            }
        
        route_options = ["route_a", "route_b", "route_c","route_d"]
        assigned_route = route_options[hash(team_id) % len(route_options)]
        
        # Initialize team data
        team_progress[team_id] = 1
        team_scores[team_id] = {"score": 0, "wrong_attempts": 0}
        team_streaks[team_id] = {"current_route": assigned_route, "streak": 0}
        team_routes[team_id] = assigned_route
        team_timers[team_id] = {
            "start_time": datetime.datetime.now(),
            "history": []
        }
        team_powerups[team_id] = []
        team_bonus_challenges[team_id] = {"active": False, "challenge_id": None}
        
        save_team_data()
        
        first_clue = clues[assigned_route][1]["question"]
        
        return {
            "response": f"🎮 Team {team_name} registered! Route {assigned_route.upper()}.\n\n📝 First clue: {first_clue}",
            "route": assigned_route,
            "clue": first_clue
        }
    except Exception as e:
        logging.error(f"Error registering team: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering team: {str(e)}")

# Update the verify_answer function in mainv4.py
@app.post("/verify_answer")
@limiter.limit("5/minute")
async def verify_answer(request: Request, data: dict):
    try:
        team_id = data.get("team_id", "").strip()
        route = data.get("route", "").strip()
        team_answer = data.get("team_answer", "").strip()
        
        if len(team_id) < 3 or len(route) == 0 or len(team_answer) < 2:
            raise HTTPException(status_code=400, detail="Invalid input data")
        
        assigned_route = team_routes.get(team_id)
        if assigned_route and assigned_route != route:
            return {
                "response": f"❌ Route mismatch! Your assigned route is {assigned_route.upper()}. Please continue with that route."
            }
            
        if team_id in team_bonus_challenges and team_bonus_challenges[team_id].get("active", False):
            return await handle_bonus_challenge(team_id, team_answer)
        
        if team_id not in team_progress:
            return {"response": "❌ Team not registered. Please register before submitting answers."}
        
        # Initialize timer with history if missing
        if team_id not in team_timers:
            team_timers[team_id] = {
                "start_time": datetime.datetime.now(),
                "history": []
            }
        elif "history" not in team_timers[team_id]:
            team_timers[team_id]["history"] = []
            
        clue_id = team_progress[team_id]
        if route not in clues or clue_id not in clues[route]:
            return {"response": "⚠️ Invalid route or clue. Please restart the game."}
        
        correct_answer = clues[route][clue_id]["answer"]
        next_clue_id = clues[route][clue_id]["next_clue"]
        
        # Use hybrid verification
        is_correct = await verify_answer_hybrid(correct_answer, team_answer)
        
        if is_correct:
            elapsed_seconds = 0
            speed_bonus = 0
            if "start_time" in team_timers[team_id]:
                now = datetime.datetime.now()
                elapsed_seconds = (now - team_timers[team_id]["start_time"]).total_seconds()
                team_timers[team_id]["start_time"] = now
                team_timers[team_id]["history"].append(elapsed_seconds)
                speed_bonus = min(settings.MAX_SPEED_BONUS, int(settings.MAX_SPEED_BONUS * (1 - elapsed_seconds/settings.TIME_LIMIT)))
            
            team_scores[team_id]["wrong_attempts"] = 0
            team_streaks[team_id]["streak"] += 1
            
            base_points = settings.BASE_POINTS + (20 * team_streaks[team_id]["streak"])
            bonus_text = ""
            
            if team_streaks[team_id]["streak"] >= 3:
                base_points *= 2
                bonus_text = "🎁 POWER-UP ACTIVATED: Double Points! "
                team_streaks[team_id]["streak"] = 0
                if "time_freeze" not in team_powerups[team_id]:
                    team_powerups[team_id].append("time_freeze")
                    bonus_text += "You've earned a Time Freeze power-up! "
                '''if random.random() < 0.5:  # 50% chance for skip clue power-up
                    team_powerups[team_id].append("skip_clue")
                    bonus_text += "You've earned a Skip Clue power-up! " '''
            
            total_points = base_points + speed_bonus
            team_scores[team_id]["score"] += total_points
            
            # Add narrative flair
            congrats_message = await generate_congrats_message(team_id, clue_id)
            
            if next_clue_id:
                response_text = (
                    f"✅ {congrats_message}\n\n{bonus_text}(Points: +{base_points}"
                    + (f", Speed Bonus: +{speed_bonus}" if speed_bonus > 0 else "")
                    + f")\n\n🔍 Proceed to the physical location for clue #{next_clue_id}!"
                )
                team_progress[team_id] = next_clue_id
            else:
                team_progress[team_id] = None
                response_text = f"🎉 CONGRATULATIONS! You've completed the treasure hunt! {bonus_text}(Points: +{base_points}"
                if speed_bonus > 0:
                    response_text += f", Speed Bonus: +{speed_bonus}"
                response_text += ")"
            
            # Bonus challenge chance (20%)
            if next_clue_id and random.random() < settings.BONUS_CHALLENGE_CHANCE:
                challenge = await generate_bonus_challenge(team_id)
                team_bonus_challenges[team_id] = {
                    "active": True,
                    "challenge": challenge,
                    "is_dynamic": challenge.get("is_dynamic", False)
                }
                response_text += f"\n\n🎮 BONUS CHALLENGE! {challenge['question']} (Worth {challenge['points']} points)"
        
        else:
            team_scores[team_id]["wrong_attempts"] += 1
            team_streaks[team_id]["streak"] = 0
            if team_scores[team_id]["wrong_attempts"] % 3 == 0:
                penalty = 10
                team_scores[team_id]["score"] = max(0, team_scores[team_id]["score"] - penalty)
                response_text = f"❌ Too many incorrect attempts! You lost {penalty} points."
            else:
                response_text = "❌ Incorrect! Keep searching and try again."
        
        save_team_data()
        return {
            "response": response_text,
            "next_clue_id": team_progress[team_id],
            "score": team_scores[team_id]["score"],
            "available_powerups": team_powerups[team_id],
            "has_bonus_challenge": team_bonus_challenges.get(team_id, {}).get("active", False)
        }
    except Exception as e:
        logging.error(f"Error verifying answer: {str(e)}")
        return {"response": f"Error processing your answer: {str(e)}"}
async def handle_bonus_challenge(team_id: str, team_answer: str) -> dict:
    try:
        if team_id not in team_bonus_challenges or not team_bonus_challenges[team_id].get("active", False):
            return {"response": "No active bonus challenge."}
            
        challenge_data = team_bonus_challenges[team_id]
        challenge = challenge_data.get("challenge")
        
        if not challenge:
            # Fallback to default challenge if needed
            challenge = {
                "question": "What is 1+1?",
                "answer": "2",
                "points": 50
            }
        
        is_correct = (team_answer.upper().strip() == challenge["answer"].upper().strip() or 
                     team_answer.upper().strip() in challenge["answer"].upper().split(","))
        points = challenge["points"]
        
        if is_correct:
            team_scores[team_id]["score"] += points
            team_bonus_challenges[team_id]["active"] = False
            clue_id = team_progress.get(team_id, 1)
            save_team_data()
            return {
                "response": f"✅ Bonus Complete! +{points} points!\n\nProceed to clue #{clue_id}.",
                "score": team_scores[team_id]["score"],
                "next_clue_id": team_progress[team_id],
                "available_powerups": team_powerups.get(team_id, []),
                "has_bonus_challenge": False
            }
        else:
            team_bonus_challenges[team_id]["active"] = False
            clue_id = team_progress.get(team_id, 1)
            return {
                "response": f"❌ Incorrect bonus answer.\n\nProceed to clue #{clue_id}.",
                "next_clue_id": team_progress[team_id],
                "score": team_scores[team_id]["score"],
                "available_powerups": team_powerups.get(team_id, []),
                "has_bonus_challenge": False
            }
    except Exception as e:
        logging.error(f"Error handling bonus: {str(e)}")
        return {"response": f"Error processing bonus: {str(e)}"}
@app.post("/buy_hint")
@limiter.limit("3/minute")
async def buy_hint(request: Request, data: dict):
    try:
        team_id = data.get("team_id", "").strip()
        route = data.get("route", "").strip()
        
        assigned_route = team_routes.get(team_id)
        if assigned_route and assigned_route != route:
            return {"response": f"❌ Route mismatch! Your route is {assigned_route.upper()}."}

        if len(team_id) < 3 or len(route) == 0:
            raise HTTPException(status_code=400, detail="Invalid team ID or route")
            
        if team_id not in team_scores:
            return {"response": "❌ Team not registered."}
        
        if team_scores[team_id]["score"] < settings.HINT_COST:
            return {"response": f"❌ Need {settings.HINT_COST} points for a hint."}
        
        team_scores[team_id]["score"] -= settings.HINT_COST
        current_clue_id = team_progress[team_id]
        
        if route not in clues or current_clue_id not in clues[route]:
            return {"response": "❌ Invalid route or clue."}
        
        answer = clues[route][current_clue_id]["answer"]
        hint_text = generate_hint_static(answer)
        
        save_team_data()
        return {
            "response": hint_text, 
            "remaining_score": team_scores[team_id]["score"]
        }
    except Exception as e:
        logging.error(f"Error getting hint: {str(e)}")
        return {"response": f"Error getting hint: {str(e)}"}

@app.post("/use_powerup")
@limiter.limit("5/minute")
async def use_powerup(request: Request, data: dict):
    try:
        team_id = data.get("team_id", "").strip()
        powerup_type = data.get("powerup_type", "").strip()
        
        if len(team_id) < 3 or len(powerup_type) == 0:
            raise HTTPException(status_code=400, detail="Missing team ID or power-up type")
            
        if team_id not in team_powerups:
            return {"response": "❌ Team not found or no power-ups."}
        
        if powerup_type == "time_freeze":
            if "time_freeze" in team_powerups[team_id]:
                if team_id in team_timers and "start_time" in team_timers[team_id]:
                    team_timers[team_id]["start_time"] += datetime.timedelta(minutes=2)
                    team_powerups[team_id].remove("time_freeze")
                    save_team_data()
                    return {"response": "⏱️ TIME FREEZE! +2 minutes."}
                else:
                    return {"response": "❌ Timer not initialized."}
            else:
                return {"response": "❌ No Time Freeze power-up."}
        
        # elif powerup_type == "skip_clue":
        #     if "skip_clue" in team_powerups[team_id]:
        #         current_route = team_routes.get(team_id)
        #         current_clue = team_progress.get(team_id, 1)
        #         if current_route in clues and current_clue in clues[current_route]:
        #             next_clue = clues[current_route][current_clue].get("next_clue")
        #             if next_clue:
        #                 team_progress[team_id] = next_clue
        #                 team_powerups[team_id].remove("skip_clue")
        #                 save_team_data()
        #                 return {"response": "⏩ CLUE SKIPPED! Next clue unlocked."}
        #             else:
        #                 return {"response": "❌ No more clues to skip!"}
        #         else:
        #             return {"response": "❌ Invalid clue progression."}
        #     else:
        #         return {"response": "❌ No Skip Clue power-up."}

        else:
            return {"response": "❌ Unknown power-up type."}
    except Exception as e:
        logging.error(f"Error using power-up: {str(e)}")
        return {"response": f"Error using power-up: {str(e)}"}


@app.get("/leaderboard")
async def get_leaderboard():
    try:
        current_leaderboard = []
        for team_id, score_data in team_scores.items():
            if team_id in team_routes:
                route = team_routes[team_id]
                progress = team_progress.get(team_id, 1)
                total_clues = len([k for k in clues[route] if k is not None])
                completion_percent = min(100, int((progress - 1) / total_clues * 100))
                avg_time = sum(team_timers.get(team_id, {}).get("history", [])) / len(team_timers.get(team_id, {}).get("history", [1])) if team_timers.get(team_id, {}).get("history") else None
                
                current_leaderboard.append({
                    "team_id": team_id,
                    "score": score_data["score"],
                    "route": route.upper(),
                    "progress": progress,
                    "completion_percent": completion_percent,
                    "average_time": avg_time,
                    "streak": team_streaks.get(team_id, {}).get("streak", 0)
                })
        
        current_leaderboard.sort(key=lambda x: x["score"], reverse=True)
        for i, team in enumerate(current_leaderboard):
            team["rank"] = i + 1
        
        return {"leaderboard": current_leaderboard}
    except Exception as e:
        logging.error(f"Error getting leaderboard: {str(e)}")
        return {"leaderboard": [], "error": str(e)}

@app.get("/team_status/{team_id}")
async def get_team_status(team_id: str):
    try:
        if team_id not in team_scores:
            raise HTTPException(status_code=404, detail="Team not found")
            
        route = team_routes.get(team_id, "unknown")
        clue_id = team_progress.get(team_id, 1)
        score = team_scores.get(team_id, {}).get("score", 0)
        current_clue = f"Clue #{clue_id} – available at physical location"
        available_powerups = team_powerups.get(team_id, [])
        has_bonus = team_bonus_challenges.get(team_id, {}).get("active", False)
        bonus_question = None
        
        if has_bonus:
            challenge_id = team_bonus_challenges[team_id].get("challenge_id")
            if challenge_id is not None and challenge_id < len(bonus_challenges):
                bonus_question = bonus_challenges[challenge_id]["question"]
        
        return {
            "team_id": team_id,
            "route": route,
            "clue_id": clue_id,
            "current_clue": current_clue,
            "score": score,
            "available_powerups": available_powerups,
            "has_active_bonus": has_bonus,
            "bonus_question": bonus_question,
            "streak": team_streaks.get(team_id, {}).get("streak", 0),
            "wrong_attempts": team_scores.get(team_id, {}).get("wrong_attempts", 0),
            "average_solve_time": sum(team_timers.get(team_id, {}).get("history", [])) / len(team_timers.get(team_id, {}).get("history", [1])) if team_timers.get(team_id, {}).get("history") else None,
            "is_game_over": team_progress.get(team_id) is None
        }
    except Exception as e:
        logging.error(f"Error getting team status: {str(e)}")
        return {"error": str(e)}

@app.post("/admin/reset_game")
async def reset_game(admin_key: str = Header(None)):
    if admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    try:
        team_progress.clear()
        team_scores.clear()
        team_streaks.clear()
        team_routes.clear()
        team_timers.clear()
        team_powerups.clear()
        team_bonus_challenges.clear()
        save_team_data()
        return {"response": "Game successfully reset"}
    except Exception as e:
        logging.error(f"Error resetting game: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting game: {str(e)}")