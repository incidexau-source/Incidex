#!/usr/bin/env python3
"""
Review Handler API
==================

Simple Flask API to handle email approval/rejection callbacks.

Run locally with: python api/review_handler.py
Or deploy as a serverless function.

Endpoints:
- GET /api/review-alert?token=xxx - Process approval/rejection
- GET /api/health - Health check
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

from flask import Flask, request, jsonify, render_template_string
from unified_alerts import ReviewProcessor

app = Flask(__name__)

# HTML templates for response pages
SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Review Processed - Incidex</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        h1 {
            color: #1a1a2e;
            margin: 0 0 16px 0;
            font-size: 24px;
        }
        p {
            color: #666;
            line-height: 1.6;
            margin: 0 0 24px 0;
        }
        .action {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 1px;
        }
        .approved { background: #d4edda; color: #155724; }
        .rejected { background: #f8d7da; color: #721c24; }
        .btn {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 20px;
        }
        .btn:hover { background: #5a6fd6; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">{{ icon }}</div>
        <h1>{{ title }}</h1>
        <p>{{ message }}</p>
        <span class="action {{ action_class }}">{{ action }}</span>
        <br>
        <a href="https://incidex.au/map.html" class="btn">View Map</a>
    </div>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Error - Incidex</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .icon { font-size: 64px; margin-bottom: 20px; }
        h1 { color: #c0392b; margin: 0 0 16px 0; font-size: 24px; }
        p { color: #666; line-height: 1.6; margin: 0; }
        .btn {
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">{{ icon }}</div>
        <h1>{{ title }}</h1>
        <p>{{ message }}</p>
        <a href="https://incidex.au" class="btn">Return Home</a>
    </div>
</body>
</html>
"""


@app.route('/api/review-alert', methods=['GET'])
def review_alert():
    """Process an approval/rejection from email link."""
    token = request.args.get('token', '')

    if not token:
        return render_template_string(
            ERROR_TEMPLATE,
            icon='',
            title='Missing Token',
            message='No review token was provided. Please use the link from your email.'
        ), 400

    processor = ReviewProcessor()
    success, message = processor.process_review(token)

    if success:
        # Determine action from message
        if 'approved' in message.lower():
            action = 'APPROVED'
            action_class = 'approved'
            icon = ''
            title = 'Item Approved'
        else:
            action = 'REJECTED'
            action_class = 'rejected'
            icon = ''
            title = 'Item Rejected'

        return render_template_string(
            SUCCESS_TEMPLATE,
            icon=icon,
            title=title,
            message=message,
            action=action,
            action_class=action_class
        )
    else:
        return render_template_string(
            ERROR_TEMPLATE,
            icon='',
            title='Review Failed',
            message=message
        ), 400


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'incidex-review-api',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint."""
    return jsonify({
        'service': 'Incidex Review API',
        'endpoints': {
            '/api/review-alert': 'Process email review tokens',
            '/api/health': 'Health check'
        }
    })


def run_local_server(port=8000):
    """Run local development server."""
    print(f"\n{'='*60}")
    print("Incidex Review API Server")
    print(f"{'='*60}")
    print(f"Running on http://localhost:{port}")
    print(f"Review endpoint: http://localhost:{port}/api/review-alert?token=xxx")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Incidex Review API Server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    args = parser.parse_args()

    run_local_server(args.port)
