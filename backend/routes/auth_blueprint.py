from flask import Blueprint, redirect, request, jsonify, session, render_template_string, current_app
import os
import requests
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_REDIRECT_URL = os.getenv("SUPABASE_REDIRECT_URL")

# This is the simple HTML/JS page that will act as the "bridge"
CALLBACK_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Processing Login...</title>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const fragment = new URLSearchParams(window.location.hash.substring(1));
            const accessToken = fragment.get('access_token');

            if (accessToken) {
                // The browser sends the token to our new backend endpoint
                fetch('/auth/token_exchange', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: accessToken })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.jwt) {
                        // For a Single Page App (SPA), you'd store this in localStorage.
                        // For this demo, we'll use it to make one request and then redirect.
                        // This shows the frontend how to use the token.
                        fetch('/api/profile', {
                            headers: {
                                'Authorization': 'Bearer ' + data.jwt
                            }
                        })
                        .then(res => res.json())
                        .then(profileData => {
                            document.body.innerHTML = `
                                <h1>Login Successful!</h1>
                                <p>Your custom application JWT has been created.</p>
                                <h3>Protected API Response:</h3>
                                <pre>${JSON.stringify(profileData, null, 2)}</pre>
                                <a href="/">Go Home</a>
                            `;
                        })

                    } else {
                        document.body.innerText = 'Error: ' + (data.error || 'Unknown error during token exchange.');
                    }
                });
            } else {
                document.body.innerText = 'Could not find access token. Login failed.';
            }
        });
    </script>
</head>
<body>
    <p>Please wait, we are securely logging you in...</p>
</body>
</html>
"""


@auth_bp.route('/login')
def login():
    redirect_url = (
        f"{SUPABASE_URL}/auth/v1/authorize"
        f"?provider=google&redirect_to={SUPABASE_REDIRECT_URL}"
    )
    return redirect(redirect_url)


@auth_bp.route('/callback')
def callback():
    return render_template_string(CALLBACK_TEMPLATE)


@auth_bp.route('/token_exchange', methods=['POST'])
def token_exchange():
    data = request.get_json()
    access_token = data.get("access_token")

    if not access_token:
        return jsonify({"error": "Access token not received"}), 400

    try:
        headers = {"Authorization": f"Bearer {access_token}", "apikey": SUPABASE_ANON_KEY}
        user_info_url = f"{SUPABASE_URL}/auth/v1/user"
        response = requests.get(user_info_url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Invalid or expired Supabase access token", "details": response.json()}), 403

        user = response.json()
        email = user.get("email")

        if not email:
            return jsonify({"error": "Email not found in user data"}), 403

        payload = {
            "email": email,
            "sub": user.get("id"),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        # Use the secret from the application config
        custom_jwt = jwt.encode(payload, current_app.config["SUPABASE_JWT_SECRET"], algorithm="HS256")

        session["jwt"] = custom_jwt
        return jsonify({"message": "Login successful", "jwt": custom_jwt})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})