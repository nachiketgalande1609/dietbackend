# app.py (updated)
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes.diet_routes import diet_bp
from routes.workout_routes import workout_bp
from routes.user_routes import user_bp
from routes.tasks_routes import tasks_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(diet_bp)
app.register_blueprint(workout_bp)
app.register_blueprint(user_bp)
app.register_blueprint(tasks_bp)  # Register the tasks blueprint

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
