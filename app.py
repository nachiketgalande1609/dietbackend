from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId
from datetime import datetime
from models import initialize_db

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]

# Initialize with sample data if empty
initialize_db(db)


@app.route("/api/diet", methods=["GET"])
def get_diet_plan():
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Find diet plan for the date
    diet_plan = db.diet_plans.find_one({"date": date_str})

    if not diet_plan:
        return jsonify({"error": "No diet plan found for this date"}), 404

    # Convert ObjectId to string
    diet_plan["_id"] = str(diet_plan["_id"])

    return jsonify(diet_plan)


@app.route("/api/diet/complete", methods=["POST"])
def mark_meal_complete():
    data = request.json
    if not data or "date" not in data or "mealTime" not in data:
        return jsonify({"error": "Date and mealTime are required"}), 400

    # Update completed meals in the database
    result = db.diet_plans.update_one(
        {"date": data["date"]}, {"$addToSet": {"completedMeals": data["mealTime"]}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Failed to update meal status"}), 400

    return jsonify({"success": True})


@app.route("/api/diet/complete", methods=["DELETE"])
def mark_meal_incomplete():
    data = request.json
    if not data or "date" not in data or "mealTime" not in data:
        return jsonify({"error": "Date and mealTime are required"}), 400

    # Remove from completed meals in the database
    result = db.diet_plans.update_one(
        {"date": data["date"]}, {"$pull": {"completedMeals": data["mealTime"]}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Failed to update meal status"}), 400

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
