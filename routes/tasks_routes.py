# tasks.py (Flask Blueprint)
from flask import Blueprint, jsonify, request
from datetime import datetime
from bson import ObjectId
from db import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


@tasks_bp.route("", methods=["GET"])
def get_tasks():
    date_str = request.args.get("date")

    try:
        if date_str:
            # Find tasks for specific date
            tasks = list(db.tasks.find({"date": date_str}))
        else:
            # Find all tasks
            tasks = list(db.tasks.find({}))

        # Convert ObjectId to string
        for task in tasks:
            task["_id"] = str(task["_id"])
            task["id"] = str(task["_id"])  # Add id field for frontend compatibility

        return jsonify({"data": tasks, "success": True, "error": None})
    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500


@tasks_bp.route("", methods=["POST"])
def create_task():
    try:
        data = request.json
        if not data or "title" not in data or "date" not in data:
            return (
                jsonify(
                    {
                        "data": None,
                        "success": False,
                        "error": "Title and date are required",
                    }
                ),
                400,
            )

        # Insert new task
        result = db.tasks.insert_one(data)
        new_task = db.tasks.find_one({"_id": result.inserted_id})
        new_task["_id"] = str(new_task["_id"])
        new_task["id"] = str(new_task["_id"])

        return jsonify({"data": new_task, "success": True, "error": None})
    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        data = request.json
        if not data:
            return (
                jsonify({"data": None, "success": False, "error": "No data provided"}),
                400,
            )

        # Update task
        result = db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": data})

        if result.modified_count == 0:
            return (
                jsonify(
                    {
                        "data": None,
                        "success": False,
                        "error": "Task not found or no changes made",
                    }
                ),
                404,
            )

        # Return updated task
        updated_task = db.tasks.find_one({"_id": ObjectId(task_id)})
        updated_task["_id"] = str(updated_task["_id"])
        updated_task["id"] = str(updated_task["_id"])

        return jsonify({"data": updated_task, "success": True, "error": None})
    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        result = db.tasks.delete_one({"_id": ObjectId(task_id)})

        if result.deleted_count == 0:
            return (
                jsonify({"data": None, "success": False, "error": "Task not found"}),
                404,
            )

        return jsonify({"data": None, "success": True, "error": None})
    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500


@tasks_bp.route("/<task_id>/completion", methods=["PATCH"])
def toggle_task_completion(task_id):
    try:
        data = request.json
        if "completed" not in data:
            return (
                jsonify(
                    {
                        "data": None,
                        "success": False,
                        "error": "Completed status is required",
                    }
                ),
                400,
            )

        # Update completion status
        result = db.tasks.update_one(
            {"_id": ObjectId(task_id)}, {"$set": {"completed": data["completed"]}}
        )

        if result.modified_count == 0:
            return (
                jsonify({"data": None, "success": False, "error": "Task not found"}),
                404,
            )

        # Return updated task
        updated_task = db.tasks.find_one({"_id": ObjectId(task_id)})
        updated_task["_id"] = str(updated_task["_id"])
        updated_task["id"] = str(updated_task["_id"])

        return jsonify({"data": updated_task, "success": True, "error": None})
    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500


@tasks_bp.route("/reorder", methods=["PATCH"])
def reorder_tasks():
    try:
        data = request.json
        if "taskId" not in data or "newIndex" not in data:
            return (
                jsonify(
                    {
                        "data": None,
                        "success": False,
                        "error": "Task ID and new index are required",
                    }
                ),
                400,
            )

        # In a real implementation, you would update the order field in the database
        # This is a simplified version that just acknowledges the reorder request
        # You might want to implement a proper ordering system with position fields

        return jsonify({"data": None, "success": True, "error": None})
    except Exception as e:
        return jsonify({"data": None, "success": False, "error": str(e)}), 500
