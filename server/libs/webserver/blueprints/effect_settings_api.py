from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_openapi import swag_from
from libs.webserver.executer import Executer
from libs.webserver.executer_base import validate_schema
from libs.webserver.messages import BadRequest, DeviceNotFound, NotFound, SettingNotFound, UnprocessableEntity
from libs.webserver.schemas.effect_settings_api_schema import (
    GET_EFFECT_SETTING_SCHEMA,
    GET_EFFECT_SETTINGS_SCHEMA,
    SET_EFFECT_SETTINGS_ALL_SCHEMA,
    SET_EFFECT_SETTINGS_SCHEMA,
)

effect_settings_api = Blueprint("effect_settings_api", __name__)


@effect_settings_api.get("/api/settings/effect")
@login_required
@swag_from("docs/effect_settings_api/get_effect_settings.yml")
def get_effect_settings():
    data_in = request.args.to_dict()

    if set(data_in) == {"device", "effect", "setting_key"}:  # Get one specific effect setting for a device.

        if not validate_schema(data_in, GET_EFFECT_SETTING_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.effect_settings_executer.get_effect_setting(
            data_in["device"],
            data_in["effect"],
            data_in["setting_key"]
        )

        if data_out is DeviceNotFound:
            return DeviceNotFound.as_response()

        if data_out is SettingNotFound:
            return SettingNotFound.as_response()

        return jsonify(data_out)

    if set(data_in) == {"device", "effect"}:  # Get all effect settings for a device.

        if not validate_schema(data_in, GET_EFFECT_SETTINGS_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.effect_settings_executer.get_effect_settings(data_in["device"], data_in["effect"])

        if data_out is DeviceNotFound:
            return DeviceNotFound.as_response()

        if data_out is SettingNotFound:
            return SettingNotFound.as_response()

        return jsonify(data_out)

    return UnprocessableEntity.as_response()


@effect_settings_api.post("/api/settings/effect")
@login_required
@swag_from("docs/effect_settings_api/set_effect_settings.yml")
def set_effect_settings():
    data_in = request.get_json()

    if set(data_in) == {"device", "effect", "settings"}:  # Set effect settings for a device.

        if not validate_schema(data_in, SET_EFFECT_SETTINGS_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.effect_settings_executer.set_effect_settings(
            data_in["device"], data_in["effect"], data_in["settings"])

        if data_out is NotFound:
            return NotFound.as_response()

        if data_out is BadRequest:
            return BadRequest.as_response()

        return jsonify(data_out)

    if set(data_in) == {"effect", "settings"}:  # Set effect settings for all devices.

        if not validate_schema(data_in, SET_EFFECT_SETTINGS_ALL_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.effect_settings_executer.set_effect_settings_for_all(
            data_in["effect"], data_in["settings"])

        if data_out is NotFound:
            return NotFound.as_response()

        if data_out is BadRequest:
            return BadRequest.as_response()

        return jsonify(data_out)

    return UnprocessableEntity.as_response()
