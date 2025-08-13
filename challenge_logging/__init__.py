from CTFd.plugins import bypass_csrf_protection
from CTFd.utils.decorators import admins_only
from flask import request, Blueprint, render_template, url_for, redirect, session
import json
from CTFd.utils import get_config, set_config
from CTFd.utils.logging import log
from CTFd.utils.user import get_current_user
import logging
import os
import sys
from flask import flash

def init_logging(app):
    logger_challenge_open = logging.getLogger("challenge_open")
    logger_challenge_open.setLevel(logging.INFO)

    log_dir = app.config["LOG_FOLDER"]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logs = {
        "challenge_open": os.path.join(log_dir, "challenge_open.log"),
    }
    try:
        for log in logs.values():
            if not os.path.exists(log):
                open(log, "a").close()

        submission_log = logging.handlers.RotatingFileHandler(
            logs["challenge_open"], maxBytes=10485760, backupCount=5
        )
        logger_challenge_open.addHandler(submission_log)
    except IOError:
        pass

    stdout = logging.StreamHandler(stream=sys.stdout)
    logger_challenge_open.addHandler(stdout)
    logger_challenge_open.propagate = 0

def get_ChallengeLog_config():
        raw = get_config("ChallengeLog")
        if raw:
            return json.loads(raw)
        return {
            "enabled": True
        }

def define_admin_page(app):
    admin_ChallengeLog = Blueprint('admin_ChallengeLog', __name__, template_folder='templates',
                                    static_folder='assets')

    @admin_ChallengeLog.route("/admin/ChallengeLog", methods=["GET", "POST"])
    @bypass_csrf_protection
    @admins_only
    def config():
        if request.method == "POST":
            ChallengeLog = {
                "enabled": 'enabled' in request.form
            }
            set_config("ChallengeLog", json.dumps(ChallengeLog))
            flash("Challenge Log Setting updated successfully.", "success")

            return redirect(url_for('admin_ChallengeLog.config'))

        ChallengeLog = get_ChallengeLog_config()
        return render_template("ChallengeLog_config.html", ChallengeLog=ChallengeLog)

    app.register_blueprint(admin_ChallengeLog)

def inject_into_routes(app):
    @app.before_request
    def enforce_ChallengeLog():
        if request.endpoint == "api.challenges_challenge" and request.method == 'GET':
            ChallengeLog=get_ChallengeLog_config()
            if ChallengeLog["enabled"]:
                ChallengeNum=request.path.replace("/api/v1/challenges/","")
                user=get_current_user()
                if user:
                    log(
                        "challenge_open",
                        format="[{date}] {ip} - {name} opened challenge {challenge}",
                        name=user.name,
                        challenge=ChallengeNum
                    )
        return

def load(app):
    define_admin_page(app)
    init_logging(app)
    inject_into_routes(app)