import os
import secrets
from hmac import compare_digest

from flask import Flask, abort, redirect, render_template, request, session, url_for
from mysql.connector import Error

from models.catalog import MODULES
from routes.web import web
from services.records import label

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32),
        OPERATOR_PASSWORD=os.getenv("APP_PASSWORD"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if config:
        app.config.update(config)

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        return session["csrf"]

    @app.before_request
    def verify_form_token():
        if request.method == "POST":
            token = session.get("csrf", "")
            submitted = request.form.get("csrf", "")
            if not token or not compare_digest(token.encode(), submitted.encode()):
                abort(400, "Form token expired or invalid. Reload the page and try again.")

    @app.after_request
    def prevent_private_caching(response):
        if session.get("operator") or request.endpoint == "web.login":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.context_processor
    def layout_context():
        return {"modules": MODULES, "csrf_token": csrf_token}

    @app.template_filter("label")
    def label_filter(value):
        return label(value)

    @app.errorhandler(Error)
    def database_error(error):
        app.logger.error("MySQL error %s", error.errno)
        return render_template("message.html", title="Database unavailable",
                               message="Check the MySQL connection and database installation."), 503

    app.register_blueprint(web)
    return app

app = create_app()
