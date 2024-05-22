from __future__ import annotations

from time import sleep

from flask_openapi import Swagger
from waitress import serve

from libs.app import create_app
from libs.webserver.blueprints.authentication_api import authentication_api
from libs.webserver.blueprints.device_api import device_api
from libs.webserver.blueprints.device_settings_api import device_settings_api
from libs.webserver.blueprints.effect_api import effect_api
from libs.webserver.blueprints.effect_settings_api import effect_settings_api
from libs.webserver.blueprints.general_api import general_api
from libs.webserver.blueprints.general_settings_api import general_settings_api
from libs.webserver.blueprints.microphone_settings_api import microphone_settings_api
from libs.webserver.blueprints.system_info_api import system_info_api
from libs.webserver.executer import Executer

# Flask DEBUG switch.
DEBUG = False


class Webserver:
    def start(self: Webserver, config_lock, notification_queue_in, notification_queue_out, effects_queue, py_audio) -> None:
        self._config_lock = config_lock
        self.notification_queue_in = notification_queue_in
        self.notification_queue_out = notification_queue_out
        self.effects_queue = effects_queue
        self._py_audio = py_audio

        self.webserver_executer = Executer(
            config_lock, notification_queue_in, notification_queue_out, effects_queue, py_audio)
        Webserver.instance = self

        self.server = create_app()

        self.server = Executer.instance.authentication_executer.add_server_authentication(self.server)

        self.server.config["TEMPLATES_AUTO_RELOAD"] = True
        webserver_port = Executer.instance.general_settings_executer.get_webserver_port()

        api_blueprints = (
            authentication_api, device_api, device_settings_api, effect_api, effect_settings_api,
            general_api, general_settings_api, system_info_api, microphone_settings_api
        )

        for blueprint in api_blueprints:
            self.server.register_blueprint(blueprint)

        self.server.config["SWAGGER"] = {
            "info": {
                "title": "MLSC API",
                "description": "API for communicating with the MLSC server. The API is based on the OpenAPI 3.1 specification.",
                "version": "2.3.0",
                "license": {
                    "name": "MIT",
                    "url": "https://github.com/TobKra96/music_led_strip_control/blob/master/LICENSE"
                }
            },
            "specs": [
                {
                    "endpoint": "openapi",
                    "route": "/openapi.json"
                }
            ],
            "specs_route": "/api/",
            "openapi": "3.1.0",
            "uiversion": 3,
            "servers": [
                {
                    "url": "/"
                }
            ],
            "components": {
                # "securitySchemes": {
                #     "ApiKeyAuth": {
                #         "type": "apiKey",
                #         "name": "x-api-key",
                #         "in": "header",
                #         "description": "Authorization header with API key"
                #     }
                # }
            },
            "ui_params": {
                # https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md
                "displayOperationId": False,
                "defaultModelExpandDepth": 5,
                "defaultModelsExpandDepth": 5,
                "displayRequestDuration": True,
                "syntaxHighlight.theme": "nord",
                "requestSnippetsEnabled": True,
                "persistAuthorization": True
            }
        }

        swagger_template = {
            "tags": [
                {
                    "name": "Auth",
                    "description": "Authentication and PIN management"
                },
                {
                    "name": "Effect",
                    "description": "Current effect controls"
                },
                {
                    "name": "Resources",
                    "description": "Static configuration data"
                },
                {
                    "name": "Settings",
                    "description": "Configuration management"
                },
                {
                    "name": "System",
                    "description": "Device and system information"
                }
            ],
            # "security": [
            #     {
            #         "ApiKeyAuth": []
            #     }
            # ]
        }

        # https://github.com/swagger-api/swagger-ui/releases
        swagger_config = Swagger.DEFAULT_CONFIG

        # Swagger UI v5.4.2 CDN and Jquery v3.7.0:
        # swagger_config["swagger_ui_bundle_js"] = "//unpkg.com/swagger-ui-dist@5.4.2/swagger-ui-bundle.js"
        # swagger_config["swagger_ui_standalone_preset_js"] = "//unpkg.com/swagger-ui-dist@5.4.2/swagger-ui-standalone-preset.js"
        # swagger_config["jquery_js"] = "//unpkg.com/jquery@3.7.0/dist/jquery.min.js"
        # swagger_config["swagger_ui_css"] = "//unpkg.com/swagger-ui-dist@5.4.2/swagger-ui.css"

        # Swagger UI v4.15.5 and Jquery v3.7.0:
        # swagger_config['swagger_ui_bundle_js'] = '/static/assets/plugins/swagger-ui-4/js/swagger-ui-bundle.js'
        # swagger_config['swagger_ui_standalone_preset_js'] = '/static/assets/plugins/swagger-ui-4/js/swagger-ui-standalone-preset.js'
        # swagger_config['jquery_js'] = '/static/assets/plugins/jquery/js/jquery.min.js'
        # swagger_config['swagger_ui_css'] = '/static/assets/plugins/swagger-ui-4/css/swagger-ui.css'

        # Swagger UI v5.4.2 and Jquery v3.7.0:
        swagger_config["swagger_ui_bundle_js"] = "/static/assets/plugins/swagger-ui/js/swagger-ui-bundle.js"
        swagger_config["swagger_ui_standalone_preset_js"] = "/static/assets/plugins/swagger-ui/js/swagger-ui-standalone-preset.js"
        swagger_config["jquery_js"] = "/static/assets/plugins/jquery/js/jquery.min.js"
        swagger_config["swagger_ui_css"] = "/static/assets/plugins/swagger-ui/css/swagger-ui.css"

        Swagger(self.server, template=swagger_template, config=swagger_config)

        if DEBUG:
            self.server.run(host="0.0.0.0", port=webserver_port, load_dotenv=False, debug=True)  # noqa: S104
        else:
            serve(self.server, host="0.0.0.0", port=webserver_port, threads=8, clear_untrusted_proxy_headers=False)  # noqa: S104
        while True:
            sleep(10)
