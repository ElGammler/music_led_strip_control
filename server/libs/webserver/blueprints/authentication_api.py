from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, logout_user
from libs.webserver.executer import Executer

authentication_api = Blueprint("authentication_api", __name__)


@authentication_api.get("/login")
def show_login_page():
    is_pin_active = Executer.instance.authentication_executer.is_pin_active()
    is_authenticated = current_user.is_authenticated

    if not is_pin_active or is_authenticated:
        return redirect(url_for("home_blueprint.index"))

    return render_template("home/login.html")


@authentication_api.post("/login")
def login():
    """Log in user
    ---
    tags:
      - Auth
    requestBody:
      content:
        application/x-www-form-urlencoded:
          schema:
            type: object
            properties:
              pin:
                description: Redirects to next page if login successful
                type: string
            required:
              - pin
      responses:
        "200":
          description: OK.
    """  # noqa: D205, D400, D415
    pin = request.form.get("pin")

    if not pin:
        flash("PIN is required")
    elif not pin.isdigit():
        flash("PIN must only contain digits")
    elif not Executer.instance.authentication_executer.validate_pin(pin):
        flash("PIN must be at least 4 digits long")
    elif pin != Executer.instance.authentication_executer.USER_PIN:
        flash("Invalid PIN")

    elif pin == Executer.instance.authentication_executer.USER_PIN:
        Executer.instance.authentication_executer.login()
        if session.get("next") is not None:
            next_page = session["next"]
            session["next"] = None
            if Executer.instance.authentication_executer.is_safe_url(next_page):
                return redirect(next_page)
        return redirect(url_for("home_blueprint.index"))

    return redirect(url_for("authentication_api.login", next=session.get("next")))


@authentication_api.get("/logout")
def logout():
    """Log out user
    ---
    tags:
      - Auth
    description:
      Redirects to login page if PIN code is enabled\n\n
      Else, redirects to dashboard
    responses:
      "200":
        description: OK
        content:
          text/html:
            schema:
              type: string.
    """  # noqa: D205, D301, D400, D415
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("authentication_api.login"))


@authentication_api.get("/api/auth/pin")
def get_pin_setting():
    """Return PIN code
    ---
    tags:
      - Auth
    description: Returning PIN is allowed only when logged in or when PIN lock is disabled
    responses:
      "200":
        description: OK
        content:
          application/json:
            schema:
              example:
                DEFAULT_PIN: str
                USE_PIN_LOCK: bool
              type: object
      "401":
        description: Unauthorized.
    """  # noqa: D205, D400, D415
    is_pin_active = Executer.instance.authentication_executer.is_pin_active()
    is_authenticated = current_user.is_authenticated

    if not is_pin_active or is_authenticated:
        data_in = Executer.instance.authentication_executer.get_pin_setting()
        data_out = {
            "DEFAULT_PIN": data_in["DEFAULT_PIN"],
            "USE_PIN_LOCK": data_in["USE_PIN_LOCK"]
        }
        return jsonify(data_out)

    return "Unauthorized", 401


@authentication_api.post("/api/auth/pin")
def set_pin_setting():
    """Set PIN code
    ---
    tags:
      - Auth
    description: Setting PIN is allowed only when logged in or when PIN lock is disabled
    requestBody:
      content:
        application/json:
          schema:
            type: string
          examples:
            example1:
              value:
                DEFAULT_PIN: 1111
                USE_PIN_LOCK: true
              summary: 4 digit active PIN
      description: 4-8 digit PIN code and active lock state
      required: true
    responses:
      "200":
        description: OK
        content:
          application/json:
            schema:
              example:
                DEFAULT_PIN: str
                USE_PIN_LOCK: bool
              type: object
      "401":
        description: Unauthorized.
    """  # noqa: D205, D400, D415
    is_pin_active = Executer.instance.authentication_executer.is_pin_active()
    is_authenticated = current_user.is_authenticated

    if not is_pin_active or is_authenticated:
        data_in = request.get_json()

        data_out = {
            "DEFAULT_PIN": data_in["DEFAULT_PIN"],
            "USE_PIN_LOCK": data_in["USE_PIN_LOCK"]
        }
        Executer.instance.authentication_executer.set_pin_setting(data_out)
        return jsonify(data_out)

    return "Unauthorized", 401


@authentication_api.delete("/api/auth/pin")
def reset_pin_setting():
    """Reset PIN code
    ---
    tags:
      - Auth
    description: Resetting PIN is allowed only when logged in or when PIN lock is disabled
    responses:
      "200":
        description: OK
        content:
          application/json:
            schema:
              example:
                DEFAULT_PIN: str
                USE_PIN_LOCK: bool
              type: object
      "401":
        description: Unauthorized.
    """  # noqa: D205, D400, D415
    is_pin_active = Executer.instance.authentication_executer.is_pin_active()
    is_authenticated = current_user.is_authenticated

    if not is_pin_active or is_authenticated:
        data_out = Executer.instance.authentication_executer.reset_pin_settings()
        return jsonify(data_out)

    return "Unauthorized", 401
