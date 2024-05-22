from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_openapi import swag_from
from libs.webserver.executer import Executer
from libs.webserver.executer_base import validate_schema
from libs.webserver.messages import (
    DeviceLimitReached,
    DeviceNotFound,
    GroupAlreadyExists,
    GroupLimitReached,
    GroupNotFound,
    UnprocessableEntity,
)
from libs.webserver.schemas.device_api_schema import CREATE_GROUP_SCHEMA, DELETE_DEVICE_SCHEMA, DELETE_GROUP_SCHEMA

device_api = Blueprint("device_api", __name__)


@device_api.get("/api/system/devices")
@login_required
@swag_from("docs/device_api/get_devices.yml")
def get_devices():
    data_out = Executer.instance.device_executer.get_devices()

    return jsonify(data_out)


@device_api.post("/api/system/devices")
@login_required
@swag_from("docs/device_api/create_device.yml")
def create_device():
    data_out = Executer.instance.device_executer.create_new_device()

    if data_out is DeviceLimitReached:
        return DeviceLimitReached.as_response()

    return jsonify(data_out)


@device_api.delete("/api/system/devices")
@login_required
@swag_from("docs/device_api/delete_device.yml")
def delete_device():
    data_in = request.get_json()

    if not validate_schema(data_in, DELETE_DEVICE_SCHEMA):
        return UnprocessableEntity.as_response()

    data_out = Executer.instance.device_executer.delete_device(data_in["device"])

    if data_out is DeviceNotFound:
        return DeviceNotFound.as_response()

    return jsonify(data_out)


@device_api.get("/api/system/groups")
@login_required
@swag_from("docs/device_api/get_groups.yml")
def get_groups():
    data_out = Executer.instance.device_executer.get_groups()

    return jsonify(data_out)


@device_api.post("/api/system/groups")
@login_required
@swag_from("docs/device_api/create_group.yml")
def create_group():
    data_in = request.get_json()

    if not validate_schema(data_in, CREATE_GROUP_SCHEMA):
        return UnprocessableEntity.as_response()

    data_out = Executer.instance.device_executer.create_new_group(data_in["group"])

    if data_out is GroupLimitReached:
        return GroupLimitReached.as_response()

    if data_out is GroupAlreadyExists:
        return GroupAlreadyExists.as_response()

    return jsonify(data_out)


@device_api.delete("/api/system/groups")
@login_required
@swag_from("docs/device_api/delete_group.yml")
def delete_group():
    data_in = request.get_json()

    if not validate_schema(data_in, DELETE_GROUP_SCHEMA):
        return UnprocessableEntity.as_response()

    data_out = Executer.instance.device_executer.delete_group(data_in["group"])

    if data_out is GroupNotFound:
        return GroupNotFound.as_response()

    return jsonify(data_out)


@device_api.patch("/api/system/groups")
@login_required
@swag_from("docs/device_api/remove_invalid_device_groups.yml")
def remove_invalid_device_groups():
    data_out = Executer.instance.device_executer.remove_invalid_device_groups()

    return jsonify(data_out)
