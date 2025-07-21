# workout_api.py
from flask import Blueprint, jsonify, request
from datetime import datetime
from bson import ObjectId
from db import db

workout_bp = Blueprint("workout", __name__, url_prefix="/api/workout")


@workout_bp.route("", methods=["GET"])
def get_workout_plan():
    date_str = request.args.get("date")
    if not date_str:
        return (
            jsonify(
                {"data": None, "success": False, "error": "Date parameter is required"}
            ),
            400,
        )

    try:
        # Find workout plan for the date
        workout_plan = db.workout_plans.find_one({"date": date_str})

        if not workout_plan:
            # Return default workout template if none exists for this date
            day_of_week = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
            template = db.workout_templates.find_one({"day": day_of_week})

            if not template:
                return jsonify({"data": None, "success": True, "error": None})

            # Create a new workout plan from template
            workout_plan = {
                "date": date_str,
                "workouts": template["categories"],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }
            db.workout_plans.insert_one(workout_plan)

        # Convert ObjectId to string and remove MongoDB _id
        workout_plan["id"] = str(workout_plan.pop("_id"))
        return jsonify({"data": workout_plan, "success": True, "error": None})

    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500


@workout_bp.route("", methods=["POST"])
def create_workout_plan():
    data = request.json
    if not data or "date" not in data or "workouts" not in data:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Date and workouts data are required",
                }
            ),
            400,
        )

    try:
        # Insert new workout plan
        result = db.workout_plans.insert_one(
            {
                "date": data["date"],
                "workouts": data["workouts"],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }
        )

        return jsonify(
            {"data": str(result.inserted_id), "success": True, "error": None}
        )

    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500


@workout_bp.route("", methods=["PUT"])
def update_workout_plan():
    data = request.json
    if not data or "date" not in data or "workouts" not in data:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Date and workouts data are required",
                }
            ),
            400,
        )

    try:
        # Update existing workout plan
        result = db.workout_plans.update_one(
            {"date": data["date"]},
            {"$set": {"workouts": data["workouts"], "updatedAt": datetime.utcnow()}},
            upsert=True,
        )

        return jsonify({"data": data["date"], "success": True, "error": None})

    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500


@workout_bp.route("/complete", methods=["POST"])
def mark_exercise_complete():
    data = request.json
    if not data or "date" not in data or "exerciseId" not in data:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Date and exerciseId are required",
                }
            ),
            400,
        )

    try:
        # Mark exercise as complete
        result = db.workout_plans.update_one(
            {"date": data["date"], "workouts.exercises.id": data["exerciseId"]},
            {"$set": {"workouts.$[].exercises.$[ex].completed": True}},
            array_filters=[{"ex.id": data["exerciseId"]}],
        )

        if result.modified_count == 0:
            return (
                jsonify(
                    {"data": None, "success": False, "error": "Exercise not found"}
                ),
                404,
            )

        return jsonify({"data": None, "success": True, "error": None})

    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500
