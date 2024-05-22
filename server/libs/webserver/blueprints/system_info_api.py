from flask import Blueprint, jsonify
from flask_login import login_required
from flask_openapi import swag_from
from libs.webserver.executer import Executer

system_info_api = Blueprint("system_info_api", __name__)


@system_info_api.get("/api/system/performance")
@login_required
@swag_from("docs/system_info_api/get_performance.yml")
def get_performance():
    data_out = Executer.instance.system_info_executer.get_system_info_performance()

    return jsonify(data_out)


@system_info_api.get("/api/system/temperature")
@login_required
@swag_from("docs/system_info_api/get_temperature.yml")
def get_temperature():
    data_out = Executer.instance.system_info_executer.get_system_info_temperature()

    return jsonify(data_out)


@system_info_api.get("/api/system/services")
@login_required
@swag_from("docs/system_info_api/get_services.yml")
def get_services():
    data_out = Executer.instance.system_info_executer.get_services()

    return jsonify(data_out)


@system_info_api.get("/api/system/services/status")
@login_required
@swag_from("docs/system_info_api/get_services_status.yml")
def get_services_status():
    data_out = Executer.instance.system_info_executer.get_system_info_services()

    return jsonify(data_out)


@system_info_api.get("/api/system/devices/status")
@login_required
@swag_from("docs/system_info_api/get_devices_status.yml")
def get_devices_status():
    data_out = Executer.instance.system_info_executer.get_system_info_device_status()

    return jsonify(data_out)


@system_info_api.get("/api/system/version")
@login_required
@swag_from("docs/system_info_api/get_version.yml")
def get_version():
    data_out = Executer.instance.system_info_executer.get_system_version()

    return jsonify(data_out)
