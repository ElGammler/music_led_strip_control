from flask import abort, render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound

from libs.app.home import blueprint
from libs.webserver.executer import Executer


@blueprint.get("/dashboard")
@blueprint.get("/")
@login_required
def index():
    devices = Executer.instance.device_executer.get_devices()
    assigned_groups = Executer.instance.device_executer.get_assigned_groups()
    return render_template("home/dashboard.html", segment="dashboard", devices=devices, groups=assigned_groups)


@blueprint.get("/system_status")
@login_required
def route_system_status():
    segment = get_segment()
    return render_template("home/system_status.html", segment=segment)


@blueprint.get("/effects/<template>")
@login_required
def route_effect_settings(template: str):
    devices = Executer.instance.device_executer.get_devices()
    assigned_groups = Executer.instance.device_executer.get_assigned_groups()

    try:
        segment = get_segment()
        return render_template(f"home/effects/{template}.html", segment=segment, devices=devices, groups=assigned_groups)
    except TemplateNotFound:
        abort(404)
    except Exception:
        abort(500)


@blueprint.get("/settings/<template>")
@login_required
def route_settings(template: str):
    devices = Executer.instance.device_executer.get_devices()
    groups = Executer.instance.device_executer.get_groups()

    try:
        segment = get_segment()
        return render_template(f"home/settings/{template}.html", segment=segment, devices=devices, groups=groups)
    except TemplateNotFound:
        abort(404)
    except Exception:
        abort(500)


def get_segment() -> str:
    """Extract current page name from request."""
    try:
        segment = request.path.split("/")[-1]
        if not segment:
            segment = "dashboard"
        return segment
    except Exception:
        return None
