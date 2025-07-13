from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import your blueprint and decorator
from auth_blueprint import auth_bp
from auth_decorator import auth_required, verify_jwt

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load secrets into the app configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY", "a-default-secret-key-for-sessions")
app.config["SUPABASE_JWT_SECRET"] = os.getenv("SUPABASE_JWT_SECRET")

# Check if the secret is loaded
if not app.config["SUPABASE_JWT_SECRET"]:
    raise ValueError("Error: SUPABASE_JWT_SECRET environment variable not set.")

# Register the authentication blueprint
app.register_blueprint(auth_bp)


# --- Routes ---

@app.route("/")
def home():
    return """
    <h1>Welcome!</h1>
    <a href="/auth/login">Login with Google</a>
    <p>After logging in, you will be redirected to the /api/profile page.</p>
    """


# Example of a protected API endpoint
@app.route("/api/profile")
@auth_required
def protected_profile():
    # The decorator has already validated the token.
    # We can optionally get the user info from the token if we need it.
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    user_payload = verify_jwt(token)

    return jsonify({
        "message": "This is a protected route. Your token is valid!",
        "user_info_from_token": user_payload
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)