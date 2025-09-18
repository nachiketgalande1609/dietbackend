# user_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from bson import ObjectId
from db import db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

# JWT Secret Key from environment variables
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRATION = os.getenv("JWT_EXPIRATION_DAYS", 7)


@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    # Validate required fields
    required_fields = [
        "email",
        "firstName",
        "lastName",
        "age",
        "birthDate",
        "weight",
        "height",
        "username",
        "password",
    ]

    if not all(field in data for field in required_fields):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "All fields are required",
                    "missing_fields": [
                        field for field in required_fields if field not in data
                    ],
                }
            ),
            400,
        )

    # Check if user already exists
    if db.users.find_one(
        {"$or": [{"email": data["email"]}, {"username": data["username"]}]}
    ):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "User with this email or username already exists",
                }
            ),
            409,
        )

    # Hash the password
    hashed_password = generate_password_hash(data["password"])

    # Create user document
    user = {
        "email": data["email"],
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "age": int(data["age"]),
        "birthDate": data["birthDate"],
        "weight": float(data["weight"]),
        "height": float(data["height"]),
        "username": data["username"],
        "password": hashed_password,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }

    # Insert user into database
    result = db.users.insert_one(user)

    # Generate JWT token
    token = jwt.encode(
        {
            "user_id": str(result.inserted_id),
            "exp": datetime.utcnow() + timedelta(days=int(JWT_EXPIRATION)),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    # Return success response with token
    return (
        jsonify(
            {
                "success": True,
                "token": token,
                "user": {
                    "id": str(result.inserted_id),
                    "email": user["email"],
                    "firstName": user["firstName"],
                    "lastName": user["lastName"],
                    "username": user["username"],
                },
            }
        ),
        201,
    )


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    # Validate required fields
    if not data or "email" not in data or "password" not in data:
        return (
            jsonify({"success": False, "error": "Email and password are required"}),
            400,
        )

    # Find user by email
    user = db.users.find_one({"email": data["email"]})

    if not user:
        return jsonify({"success": False, "error": "Email not registered"}), 401

    # Check password
    if not check_password_hash(user["password"], data["password"]):
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    # Generate JWT token
    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "exp": datetime.utcnow() + timedelta(days=int(JWT_EXPIRATION)),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    # Return success response with token
    return (
        jsonify(
            {
                "success": True,
                "token": token,
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "firstName": user["firstName"],
                    "lastName": user["lastName"],
                    "username": user["username"],
                },
            }
        ),
        200,
    )
