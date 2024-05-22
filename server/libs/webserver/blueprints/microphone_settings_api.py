from flask import Blueprint, jsonify, request
from flask_login import login_required
from libs.webserver.executer import Executer

microphone_settings_api = Blueprint("microphone_settings_api", __name__)


@microphone_settings_api.get("/api/settings/microphone/volume")
@login_required
def microphone_get_volume():
    """Return microphone volume
    ---
    tags:
      - Settings
    deprecated: true
    responses:
      "200":
        description: OK
        content:
          application/json:
            schema:
              example:
                error: str
                level: int
                output: str
                returncode: int
              type: object.
    """  # noqa: D205, D400, D415
    data_out = Executer.instance.microphone_settings_executer.microphone_get_volume()

    return jsonify(data_out)


@microphone_settings_api.post("/api/settings/microphone/volume")
@login_required
def microphone_set_volume():
    """Set microphone volume
    ---
    tags:
      - Settings
    deprecated: true
    requestBody:
      content:
        application/json:
          schema:
            type: string
          examples:
            example1:
              value:
                level: 50
              summary: Set volume to 50
      description: Volume level to set
      required: true
    responses:
      "200":
        description: OK
        content:
          application/json:
            schema:
              example:
                error: str
                output: str
                returncode: int
              type: object
      "422":
        description: Unprocessable Entity.
    """  # noqa: D205, D400, D415
    data_in = request.get_json()

    if not Executer.instance.effect_executer.validate_data_in(data_in, ("level",)):
        return jsonify("Unprocessable Entity."), 422

    data_out = Executer.instance.microphone_settings_executer.microphone_set_volume(data_in["level"])

    return jsonify(data_out)
