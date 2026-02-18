# Language: Python 3.11
# Packages: flask==3.1.0

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional

from flask import Flask, render_template, request, redirect, url_for, session, flash
from app.auth import AuthService, User

app = Flask(__name__)
app.secret_key = "demo-secret-key-change-in-production"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize auth service
auth_service = AuthService(max_failed_attempts=5)


def reset_auth_service():
    """Reset auth service for testing."""
    global auth_service, lockout_times
    auth_service = AuthService(max_failed_attempts=5)
    lockout_times = {}
    # Pre-register demo user
    auth_service.register("demo", "demo")


# Pre-register demo user
reset_auth_service()

# Track lockout times
lockout_times: dict[str, datetime] = {}


def is_locked_out(username: str) -> bool:
    """Check if user is still in lockout period (5 minutes)."""
    if username in lockout_times:
        elapsed = datetime.now() - lockout_times[username]
        if elapsed < timedelta(minutes=5):
            return True
        else:
            # Lockout expired, remove it
            del lockout_times[username]
    return False


@app.route('/')
def index():
    """Redirect to login or dashboard."""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Check if user is locked out
        if is_locked_out(username):
            return render_template('login.html',
                                 error="Account temporarily locked",
                                 login_disabled=True)

        # Attempt login
        result = auth_service.login(username, password)

        if result.get('ok'):
            # Success - create session
            session['username'] = username
            session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            # Failed login
            error_msg = result.get('error', 'Invalid email or password')

            # If account is locked, record lockout time
            if error_msg == "Account locked":
                lockout_times[username] = datetime.now()
                return render_template('login.html',
                                     error="Account temporarily locked",
                                     login_disabled=True)

            return render_template('login.html', error=error_msg)

    # GET request
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """Protected dashboard page."""
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'])


@app.route('/admin')
def admin():
    """Protected admin page - requires specific permission."""
    if 'username' not in session:
        return redirect(url_for('login'))

    # For demo, only 'admin' user can access
    if session.get('username') != 'admin':
        return redirect(url_for('login'))

    return render_template('admin.html', username=session['username'])


@app.route('/logout')
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for('login'))


@app.route('/reset-test-state', methods=['POST'])
def reset_test_state():
    """Reset auth service state for testing. Only for testing!"""
    if app.debug:  # Only allow in debug mode
        reset_auth_service()
        return {"ok": True, "message": "State reset"}, 200
    return {"ok": False, "message": "Not allowed"}, 403


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
