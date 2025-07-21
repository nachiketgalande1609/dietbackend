from flask import Blueprint, jsonify, request
from datetime import datetime
from bson import ObjectId
from db import db

diet_bp = Blueprint("diet", __name__, url_prefix="/api/diet")


@diet_bp.route("", methods=["GET"])
def get_diet_plan():
    date_str = request.args.get("date")
    if not date_str:
        return (
            jsonify(
                {"data": None, "success": False, "error": "Date parameter is required"}
            ),
            400,
        )

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Invalid date format. Use YYYY-MM-DD",
                }
            ),
            400,
        )

    # Find diet plan for the date
    diet_plan = db.diet_plans.find_one({"date": date_str})

    if not diet_plan:
        return jsonify({"data": None, "success": True, "error": None})

    # Convert ObjectId to string
    diet_plan["_id"] = str(diet_plan["_id"])

    return jsonify({"data": diet_plan, "success": True, "error": None})


@diet_bp.route("/complete", methods=["POST"])
def mark_meal_complete():
    data = request.json
    if not data or "date" not in data or "mealTime" not in data:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Date and mealTime are required",
                }
            ),
            400,
        )

    # Update completed meals in the database
    result = db.diet_plans.update_one(
        {"date": data["date"]}, {"$addToSet": {"completedMeals": data["mealTime"]}}
    )

    if result.modified_count == 0:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Failed to update meal status",
                }
            ),
            400,
        )

    return jsonify({"data": None, "success": True, "error": None})


@diet_bp.route("/incomplete", methods=["DELETE"])
def mark_meal_incomplete():
    data = request.json
    if not data or "date" not in data or "mealTime" not in data:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Date and mealTime are required",
                }
            ),
            400,
        )

    # Remove from completed meals in the database
    result = db.diet_plans.update_one(
        {"date": data["date"]}, {"$pull": {"completedMeals": data["mealTime"]}}
    )

    if result.modified_count == 0:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Failed to update meal status",
                }
            ),
            400,
        )

    return jsonify({"data": None, "success": True, "error": None})


@diet_bp.route("/update", methods=["PUT"])
def update_diet_plan():
    data = request.json
    if not data or "date" not in data or "meals" not in data:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "Date and meals data are required",
                }
            ),
            400,
        )

    # Update or insert the diet plan
    result = db.diet_plans.update_one(
        {"date": data["date"]},
        {
            "$set": {
                "meals": data["meals"],
                "dailyTotal": data.get("dailyTotal", {}),
                "lastUpdated": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    if result.modified_count == 0 and not result.upserted_id:
        return (
            jsonify(
                {"data": None, "success": False, "error": "Failed to update diet plan"}
            ),
            400,
        )

    return jsonify({"data": None, "success": True, "error": None})


@diet_bp.route("/", methods=["DELETE"])
def delete_diet_plan():
    date_str = request.args.get("date")
    if not date_str:
        return (
            jsonify(
                {"data": None, "success": False, "error": "Date parameter is required"}
            ),
            400,
        )

    result = db.diet_plans.delete_one({"date": date_str})

    if result.deleted_count == 0:
        return (
            jsonify(
                {
                    "data": None,
                    "success": False,
                    "error": "No diet plan found for this date",
                }
            ),
            404,
        )

    return jsonify({"data": None, "success": True, "error": None})
