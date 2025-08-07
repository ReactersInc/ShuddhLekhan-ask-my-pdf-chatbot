import bcrypt
from database.supabase_client import get_db_connection

def create_user(email, name, password):
    conn = get_db_connection()
    cur = conn.cursor()

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        cur.execute("INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                    (email, name, password_hash))
        conn.commit()
        return {"status": "success", "message": "User created"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cur.close()
        conn.close()


def authenticate_user(email, password):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
        result = cur.fetchone()
        if not result:
            return {"status": "error", "message": "User not found"}

        stored_hash = result[0]
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return {"status": "success", "message": "Login successful"}
        else:
            return {"status": "error", "message": "Incorrect password"}
    finally:
        cur.close()
        conn.close()
