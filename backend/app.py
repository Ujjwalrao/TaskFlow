"""
TaskFlow — Backend Entrypoint
A single-user-friendly, no-login productivity OS.
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from database.db import init_db

load_dotenv()

from routes.tasks import tasks_bp
from routes.habits import habits_bp
from routes.goals import goals_bp
from routes.workspace import workspace_bp
from routes.search import search_bp
from routes.export import export_bp
from routes.feedback import feedback_bp
from routes.notifications import notifications_bp
from routes.integrations import integrations_bp


def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)

    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(habits_bp, url_prefix="/api/habits")
    app.register_blueprint(goals_bp, url_prefix="/api/goals")
    app.register_blueprint(workspace_bp, url_prefix="/api/workspace")
    app.register_blueprint(search_bp, url_prefix="/api/search")
    app.register_blueprint(export_bp, url_prefix="/api/export")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(integrations_bp, url_prefix="/api/integrations")

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
