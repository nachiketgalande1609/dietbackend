from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes.diet_routes import diet_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(diet_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
