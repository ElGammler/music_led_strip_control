from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_openapi import swag_from
from libs.webserver.executer import Executer
from libs.webserver.executer_base import validate_schema
from libs.webserver.messages import DeviceNotFound, SettingNotFound, UnprocessableEntity
from libs.webserver.schemas.device_settings_api_schema import (
    ALL_DEVICE_SETTINGS_SCHEMA,
    DEVICE_SETTINGS_WITH_EXCL_SCHEMA,
    GET_ALL_OUTPUT_SETTINGS_SCHEMA,
    GET_OUTPUT_SETTING_SCHEMA,
    ONE_DEVICE_SETTING_SCHEMA,
    SET_DEVICE_SETTINGS_SCHEMA,
    SET_OUTPUT_SETTINGS_SCHEMA,
)

device_settings_api = Blueprint("device_settings_api", __name__)


@device_settings_api.get("/api/settings/device")
@login_required
@swag_from("docs/device_settings_api/get_device_settings.yml")
def get_device_settings():
    data_in = request.args.to_dict()

    if set(data_in) == {"device"}:  # Get all device settings of one device.

        if not validate_schema(data_in, ALL_DEVICE_SETTINGS_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.device_settings_executer.get_device_settings(data_in["device"])

        if data_out is DeviceNotFound:
            return DeviceNotFound.as_response()

        return jsonify(data_out)

    if set(data_in) == {"device", "setting_key"}:  # Get one specific device setting of one device.

        if not validate_schema(data_in, ONE_DEVICE_SETTING_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.device_settings_executer.get_device_setting(data_in["device"], data_in["setting_key"])

        if data_out is DeviceNotFound:
            return DeviceNotFound.as_response()

        return jsonify(data_out)

    if set(data_in) == {"device", "excluded_key"}:  # Get all settings of one device excluding a specific setting.

        if not validate_schema(data_in, DEVICE_SETTINGS_WITH_EXCL_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.device_settings_executer.get_device_settings(data_in["device"], data_in["excluded_key"])

        if data_out is DeviceNotFound:
            return DeviceNotFound.as_response()

        return jsonify(data_out)

    return UnprocessableEntity.as_response()


@device_settings_api.post("/api/settings/device")
@login_required
@swag_from("docs/device_settings_api/set_device_settings.yml")
def set_device_settings():
    data_in = request.get_json()

    if not validate_schema(data_in, SET_DEVICE_SETTINGS_SCHEMA):
        return UnprocessableEntity.as_response()

    data_out = Executer.instance.device_settings_executer.set_device_settings(data_in["device"], data_in["settings"])

    if data_out is DeviceNotFound:
        return DeviceNotFound.as_response()

    return jsonify(data_out)


@device_settings_api.get("/api/settings/device/output-type")
@login_required
@swag_from("docs/device_settings_api/get_output_type_device_settings.yml")
def get_output_type_device_settings():
    data_in = request.args.to_dict()

    if set(data_in) == {"device"}:  # Get all output type settings of a device.

        if not validate_schema(data_in, GET_ALL_OUTPUT_SETTINGS_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.device_settings_executer.get_all_output_type_settings(data_in["device"])

        if data_out is DeviceNotFound:
            return DeviceNotFound.as_response()

        return jsonify(data_out)

    if set(data_in) == {"device", "output_type_key", "setting_key"}:  # Get one specific output type setting of a device.

        if not validate_schema(data_in, GET_OUTPUT_SETTING_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.device_settings_executer.get_output_type_device_setting(
            data_in["device"],
            data_in["output_type_key"],
            data_in["setting_key"]
        )

        if data_out is DeviceNotFound:
            return DeviceNotFound.as_response()

        if data_out is SettingNotFound:
            return SettingNotFound.as_response()

        return jsonify(data_out)

    return UnprocessableEntity.as_response()


@device_settings_api.post("/api/settings/device/output-type")
@login_required
@swag_from("docs/device_settings_api/set_output_type_device_settings.yml")
def set_output_type_device_settings():
    data_in = request.get_json()

    if not validate_schema(data_in, SET_OUTPUT_SETTINGS_SCHEMA):
        return UnprocessableEntity.as_response()

    data_out = Executer.instance.device_settings_executer.set_output_type_device_settings(
        data_in["device"],
        data_in["output_type_key"],
        data_in["settings"]
    )

    if data_out is DeviceNotFound:
        return DeviceNotFound.as_response()

    if data_out is SettingNotFound:
        return SettingNotFound.as_response()

    return jsonify(data_out)
