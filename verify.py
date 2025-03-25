from datetime import datetime, timezone, timedelta
import mysql.connector
import bcrypt
from flask import Flask, request, render_template_string
import os
from dotenv import load_dotenv, find_dotenv
# Load environment variables
load_dotenv(find_dotenv(), override=True)
public_url = "https://0878-103-228-147-209.ngrok-free.app"  # Add your current URL
os.environ["PUBLIC_URL"] = public_url
print(f"Manually set PUBLIC_URL: {public_url}")
from email_utils import generate_token



app = Flask(__name__)

@app.route("/verify")
def verify():
    token = request.args.get("token")
    if not token:
        return "Missing token", 400

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="riyranagi007*",
            database="churn_db"
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM User
            WHERE verification_token = %s
              AND verified = FALSE
              AND token_expiration > NOW()
            """,
            (token,)
        )
        user = cursor.fetchone()

        if user:
            cursor.execute(
                """
                UPDATE User
                SET verified = TRUE,
                    verification_token = NULL,
                    token_expiration = NULL
                WHERE verification_token = %s
                """,
                (token,)
            )
            conn.commit()
            message = "Email verified successfully! You can now log in."
        else:
            message = "Invalid or expired token."
    except Exception as e:
        message = f"Error during verification: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template_string("<h3>{{ message }}</h3>", message=message)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token")
    if not token:
        return "Missing token", 400

    if request.method == "GET":
        # Improved HTML form with show password functionality.
        form_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>Reset Password</title>
          <style>
            body {{
              background-color: #f2f2f2;
              font-family: Arial, sans-serif;
              margin: 0;
              padding: 0;
            }}
            .container {{
              max-width: 400px;
              margin: 80px auto;
              background-color: #fff;
              border-radius: 8px;
              padding: 30px;
              box-shadow: 0 2px 10px rgba(0,0,0,0.1);
              text-align: center;
            }}
            h3 {{
              color: #333;
            }}
            input[type="password"],
            input[type="text"] {{
              width: 100%;
              padding: 12px 20px;
              margin: 10px 0;
              border: 1px solid #ccc;
              border-radius: 4px;
              box-sizing: border-box;
            }}
            input[type="submit"] {{
              width: 100%;
              background-color: #4CAF50;
              color: white;
              padding: 14px 20px;
              margin: 10px 0;
              border: none;
              border-radius: 4px;
              cursor: pointer;
            }}
            input[type="submit"]:hover {{
              background-color: #45a049;
            }}
            .checkbox-container {{
              text-align: left;
              margin: 10px 0;
            }}
          </style>
        </head>
        <body>
          <div class="container">
            <h3>Reset Your Password</h3>
            <form method="POST">
              <input type="hidden" name="token" value="{token}"/>
              <input type="password" id="new_password" name="new_password" placeholder="New Password" required/>
              <div class="checkbox-container">
                <label><input type="checkbox" onclick="togglePassword()"> Show Password</label>
              </div>
              <input type="submit" value="Reset Password"/>
            </form>
            <script>
              function togglePassword() {{
                var x = document.getElementById("new_password");
                if (x.type === "password") {{
                  x.type = "text";
                }} else {{
                  x.type = "password";
                }}
              }}
            </script>
          </div>
        </body>
        </html>
        """
        return render_template_string(form_html)

    else:
        # Process the new password submission
        new_password = request.form.get("new_password")
        if not new_password or len(new_password) < 8:
            return "Password must be at least 8 characters long", 400

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="riyranagi007*",
                database="churn_db"
            )
            cursor = conn.cursor(dictionary=True)
            # Validate the token using the reset token fields.
            query = """
            SELECT * FROM User
            WHERE reset_token = %s
              AND reset_token_expiration > NOW()
            """
            cursor.execute(query, (token,))
            user = cursor.fetchone()
            if not user:
                return "Invalid or expired token", 400

            # Hash the new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Update the user's password and clear the reset token & expiration time
            update_query = """
            UPDATE User
            SET password = %s,
                reset_token = NULL,
                reset_token_expiration = NULL
            WHERE reset_token = %s
            """
            cursor.execute(update_query, (hashed_password, token))
            conn.commit()

            return "Password has been reset successfully!"
        except Exception as e:
            return f"Error updating password: {e}", 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

@app.route("/request_reset", methods=["POST"])
def request_reset():
    email = request.form.get("email")
    if not email:
        return "Missing email", 400

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="riyranagi007*",
            database="churn_db"
        )
        cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for easier access
        
        # First, check if the email exists in the database
        cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            # Don't reveal that the email doesn't exist (security best practice)
            return "If your email is registered, you will receive password reset instructions shortly."
        
        reset_token = generate_token()
        # Use timezone-aware datetime for expiration.
        reset_token_expiration = datetime.now(timezone.utc) + timedelta(hours=1)
        
        update_query = """
            UPDATE User SET reset_token = %s, reset_token_expiration = %s
            WHERE email = %s
        """
        cursor.execute(update_query, (reset_token, reset_token_expiration, email))
        conn.commit()

        # Send an actual email with the reset link
        try:
            reset_link = f"{public_url}/reset_password?token={reset_token}"
            email_subject = "Password Reset Instructions"
            email_body = f"""
Hello,

You requested a password reset for your Churn Prediction App account.
Please click the following link to reset your password:

{reset_link}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

Best regards,
The Churn Prediction Team
            """
            
            # Add detailed logging before sending email
            print(f"DEBUG: About to send email to {email} with reset link {reset_link}")
            
            # Use the send_email function from email_utils
            from email_utils import send_email
            send_email(email, email_subject, email_body)
            
            print("DEBUG: Email sent successfully")
            return "If your email is registered, you will receive password reset instructions shortly."
        except Exception as e:
            # Add more detailed error logging
            import traceback
            print(f"ERROR: Failed to send reset email: {e}")
            print(f"ERROR: Traceback: {traceback.format_exc()}")
            return f"Error processing request: {str(e)}", 500
            
    except Exception as e:
        # Add more detailed error logging
        import traceback
        print(f"ERROR: Database operation failed: {e}")
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return f"Error requesting password reset: {str(e)}", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    # For local testing; bind to 0.0.0.0 so ngrok can access.
    app.run(debug=True, host="0.0.0.0", port=5000)