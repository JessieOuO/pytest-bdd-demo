#!/usr/bin/env python3
"""
Simple script to run the Flask web server for UI testing.

Usage:
    python run_server.py
"""

if __name__ == '__main__':
    from src.app.web import app
    print("Starting Flask server on http://localhost:3000")
    print("Press Ctrl+C to stop")
    print("\nDemo credentials:")
    print("  Username: demo")
    print("  Password: demo")
    app.run(host='0.0.0.0', port=3000, debug=True)
