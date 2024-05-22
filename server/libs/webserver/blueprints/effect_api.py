from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_openapi import swag_from
from libs.webserver.executer import Executer
from libs.webserver.executer_base import validate_schema
from libs.webserver.messages import DeviceNotFound, DuplicateItem, UnprocessableEntity
from libs.webserver.schemas.effect_api_schema import (
    DEVICE_ACTIVE_EFFECT_SCHEMA,
    DEVICE_CYCLE_STATUS_SCHEMA,
    SET_ACTIVE_EFFECT_ALL_SCHEMA,
    SET_ACTIVE_EFFECT_MULT_SCHEMA,
    SET_ACTIVE_EFFECT_SCHEMA,
)

effect_api = Blueprint("effect_api", __name__)


@effect_api.get("/api/effect/active")
@login_required
@swag_from("docs/effect_api/get_active_effect.yml")
def get_active_effect():
    data_in = request.args.to_dict()

    if set(data_in) == {"device"}:  # Get the active effect for a specific device.

        if not validate_schema(data_in, DEVICE_ACTIVE_EFFECT_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.effect_executer.get_active_effect(data_in["device"])

        if data_out is DeviceNotFound:
            return DeviceNotFound.as_response()

        return jsonify(data_out)

    if not set(data_in):  # Get the active effects for all devices.
        data_out = Executer.instance.effect_executer.get_active_effects()

        return jsonify(data_out)

    return UnprocessableEntity.as_response()


@effect_api.post("/api/effect/active")
@login_required
@swag_from("docs/effect_api/set_active_effect.yml")
def set_active_effect():
    data_in = request.get_json()
    data_out = {}

    if set(data_in) == {"device", "effect"}:  # Set effect for one device.

        if not validate_schema(data_in, SET_ACTIVE_EFFECT_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.effect_executer.set_active_effect(data_in["device"], data_in["effect"])

    elif set(data_in) == {"devices"}:  # Set effect for multiple devices.
        if not validate_schema(data_in, SET_ACTIVE_EFFECT_MULT_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.effect_executer.set_active_effect_for_multiple(data_in["devices"])

    elif set(data_in) == {"effect"}:  # Set effect for all devices.
        if not validate_schema(data_in, SET_ACTIVE_EFFECT_ALL_SCHEMA):
            return UnprocessableEntity.as_response()

        data_out = Executer.instance.effect_executer.set_active_effect_for_all(data_in["effect"])

    else:
        return UnprocessableEntity.as_response()

    if data_out is DuplicateItem:
        return DuplicateItem.as_response()

    if data_out is DeviceNotFound:
        return DeviceNotFound.as_response()

    return jsonify(data_out)


@effect_api.get("/api/effect/cycle-status")
@login_required
@swag_from("docs/effect_api/get_cycle_status.yml")
def get_cycle_status():
    data_in = request.args.to_dict()

    if not validate_schema(data_in, DEVICE_CYCLE_STATUS_SCHEMA):
        return UnprocessableEntity.as_response()

    data_out = Executer.instance.effect_executer.is_cycle_job_running(data_in["device"])

    if data_out is DeviceNotFound:
        return DeviceNotFound.as_response()

    return jsonify(data_out)
