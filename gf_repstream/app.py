from flask import Flask, request, jsonify, make_response
from flask_session import Session

import argparse
import logging
import pkg_resources
from enum import Enum
from systemd import journal
from cli import SRepeater

__author__ = "Leonardo Hax Damiani"
__date_created__ = "2020-12-02"
__credits__ = "Christian M. Schlepuetz"
__copyright__ = "Copyright (c) 2021, Paul Scherrer Institut"
__docformat__ = "restructuredtext en"


class State(Enum):
    INITIALIZED = 0
    RUNNING = 1
    ERROR = 2
    STOPPED = 3


_logger = logging.getLogger("RestStreamRepeater")
_logger.addHandler(journal.JournaldLogHandler())


app = Flask("RestStreamRepeater")
app.config["state"] = None
app.config['valid_config'] = False
app.config['valid_writer_config'] = False
app.config['std_det_output'] = False
Session(app)

def start_rest_api(port, config_file):
    """Function that starts the rest server and listen to the commands that control the stream repeater service.

    Args:
        port (int): Port that the stream repeater REST api will listen to
        config_file (str): Path to stream repeater config file

    """
    # FIXME: static file should be loaded from the package via pkg_resources prior to deployment
    # repeater = SRepeater(config_file='./static/repstream_config.json')
    repeater = SRepeater(config_file=config_file)
    app.config['valid_config'] = True
    app.config["state"] = State.STOPPED
    app.config['std_det_output'] = repeater.is_using_std_det()

    @app.route("/initialize", methods=["POST"])
    def configure():
        """Applies the configuration to start the stream repeater.

        Returns:
            HTTP response with status of the request, configuration and state of the stream repeater.
        """
        if app.config["state"] in [State.STOPPED, State.INITIALIZED, State.ERROR]:
            try:
                repeater.set_event()
                config = repeater.load_config()
                app.config['valid_config'] = True
                if app.config['valid_config'] and (app.config['valid_writer_config'] or not app.config['std_det_output']):
                    app.config["state"] = State.INITIALIZED
            except BaseException as err:
                return make_response(
                    jsonify(
                        {
                            "response": "error",
                            "error": f"Unexpected {err=}, {type(err)=}",
                        }
                    ),
                    200,
                )
            state_return = (app.config["state"].name, app.config["state"].value)
            _logger.debug(f"Service Rest Stream Repeater: {state_return}")
            return make_response(
                jsonify(
                    {"response": "success", "state": state_return, "config": config}
                ),
                200,
            )
        else:
            state_return = (app.config["state"].name, app.config["state"].value)
            return make_response(
                jsonify(
                    {
                        "response": "error",
                        "error": f"Streamer in state {state_return[0]} can not be initialized.",
                        "state": state_return,
                    }
                ),
                200,
            )

    @app.route("/get_status", methods=["GET"])
    def get_status():
        """Gets the configuration from the stream repeater object.

        Returns:
            HTTP response with status of the request, configuration and state of the stream repeater.
        """

        try:
            config = repeater.get_config()
            state_return = (app.config["state"].name, app.config["state"].value)
            _logger.debug(f"Service Rest Stream Repeater: {state_return}")
        except BaseException as err:
            return make_response(
                jsonify(
                    {"response": "error", "error": f"Unexpected {err=}, {type(err)=}"}
                ),
                200,
            )
        return make_response(
            jsonify({"response": "success", "state": state_return, "config": config}),
            200,
        )

    @app.route("/get_state", methods=["GET"])
    def get_state():
        """GET request to load the state from the stream repeater object.

        Returns:
            HTTP response with status of the request and state of the stream repeater object.
        """
        try:
            state_return = (app.config["state"].name, app.config["state"].value)
            _logger.debug(f"Service Rest Stream Repeater: {state_return}")
        except BaseException as err:
            app.config["state"] = State.ERROR
            return make_response(
                jsonify(
                    {"response": "error", "error": f"Unexpected {err=}, {type(err)=}"}
                ),
                200,
            )
        return make_response(
            jsonify({"response": "success", "state": state_return}),
            200,
        )

    @app.route("/set_config_from_dict", methods=["POST"])
    def set_config_from_dict():
        """POST request to set a new configuration values using a dictionary into the stream repeater object.

        Returns:
            HTTP response with status of the request and the state of the stream repeater object.
        """
        if app.config["state"] in [State.STOPPED, State.INITIALIZED, State.ERROR]:
            dict_config = request.json
            try:
                repeater.set_event()
                app.config['valid_config'] = repeater.set_config_dict(dict_config)
                app.config['std_det_output'] = repeater.is_using_std_det()
                if app.config['valid_config'] and (app.config['valid_writer_config'] or not app.config['std_det_output']):
                    app.config["state"] = State.INITIALIZED
                _logger.debug(
                    f"Service Rest Stream Repeater: set_config_from_dict {dict_config}"
                )
            except BaseException as err:
                app.config["state"] = State.ERROR
                return make_response(
                    jsonify(
                        {"response": "error", "error": f"Unexpected {err=}, {type(err)=}"}
                    ),
                    200,
                )
            return make_response(
                jsonify(
                    {
                        "response": "success",
                        "state": (app.config["state"].name, app.config["state"].value),
                    }
                ),
                200,
            )
        else:
            state_return = (app.config["state"].name, app.config["state"].value)
            return make_response(
                jsonify(
                    {
                        "response": "error",
                        "error": f"Streamer in state {state_return[0]} can not be configured.",
                        "state": state_return,
                    }
                ),
                200,
            )

    @app.route("/set_config_from_file", methods=["POST"])
    def set_config_from_file():
        """POST request to set a new configuration values using a config file into the stream repeater object.

        Returns:
            HTTP response with status of the request and the state of the stream repeater object.
        """
        if app.config["state"] in [State.STOPPED, State.INITIALIZED, State.ERROR]:
            config_file = request.json
            try:
                new_config_file = config_file["config_file"]
                repeater.set_config_file(new_config_file)
                app.config['std_det_output'] = repeater.is_using_std_det()
                app.config['valid_config'] = True
                if app.config['valid_config'] and (app.config['valid_writer_config'] or not app.config['std_det_output']):
                    app.config["state"] = State.INITIALIZED
                
                _logger.debug(
                    f"Service Rest Stream Repeater: Initialized with the config file {new_config_file}"
                )
            except BaseException as err:
                app.config["state"] = State.ERROR
                return make_response(
                    jsonify(
                        {"response": "error", "error": f"Unexpected {err=}, {type(err)=}"}
                    ),
                    200,
                )
            return make_response(
                jsonify(
                    {
                        "response": "success",
                        "state": (app.config["state"].name, app.config["state"].value),
                    }
                ),
                200,
            )
        else:
            state_return = (app.config["state"].name, app.config["state"].value)
            return make_response(
                jsonify(
                    {
                        "response": "error",
                        "error": f"Streamer in state {state_return[0]} can not be configured.",
                        "state": state_return,
                    }
                ),
                200,
            )

    @app.route("/set_writer_config_rest", methods=["POST"])
    def set_writer_config_rest():
        """POST request to set the writer configurations in the streamer.
        """
        if app.config["state"] in [State.STOPPED, State.INITIALIZED, State.ERROR] and 
            app.config['std_det_output']:
            writer_dict = request.json
            try:
                app.config['valid_writer_config'] = repeater.set_writer_config(writer_dict)
                if app.config['valid_config'] and (app.config['valid_writer_config'] or not app.config['std_det_output']):
                    app.config["state"] = State.INITIALIZED
                _logger.debug(
                    f"Service Rest Stream Repeater: Writer configuration {writer_dict}"
                )
            except BaseException as err:
                app.config["state"] = State.ERROR
                return make_response(
                    jsonify(
                        {"response": "error", "error": f"Unexpected {err=}, {type(err)=}"}
                    ),
                    200,
                )
            return make_response(
                jsonify(
                    {
                        "response": "success",
                        "state": (app.config["state"].name, app.config["state"].value),
                    }
                ),
                200,
            )
        else:
            if not app.config['std_det_output']:
                state_return = (app.config["state"].name, app.config["state"].value)
                return make_response(
                    jsonify(
                        {
                            "response": "error",
                            "error": f"Streamer has no std-det-writer stream to be configured.",
                            "state": state_return,
                        }
                    ),
                    200,
                )

            else:
                state_return = (app.config["state"].name, app.config["state"].value)
                return make_response(
                    jsonify(
                        {
                            "response": "error",
                            "error": f"Streamer in state {state_return[0]} can not be configured.",
                            "state": state_return,
                        }
                    ),
                    200,
                )

    @app.route("/start", methods=["POST"])
    def start_streamer():
        """POST request to start a new stream using the initialized stream repeater object.

        Returns:
            HTTP response with status of the request and the state of the stream repeater object.
        """
        if app.config["state"] == State.INITIALIZED and (app.config['valid_writer_config']  or not app.config['std_det_output']) and app.config['valid_config']: 
            try:
                _logger.debug(f"Service Rest Stream Repeater: starting...")
                repeater.start()
                app.config["state"] = State.RUNNING
                app.config['valid_writer_config'] = False
                app.config['valid_config'] = False
            except BaseException as err:
                app.config["state"] = State.ERROR
                return make_response(
                    jsonify(
                        {
                            "response": "error",
                            "error": f"Unexpected {err=}, {type(err)=}",
                        }
                    ),
                    200,
                )
            state_return = (app.config["state"].name, app.config["state"].value)
            return make_response(
                jsonify({"response": "success", "state": state_return}),
                200,
            )
        else:
            state_return = (app.config["state"].name, app.config["state"].value)
            return make_response(
                jsonify(
                    {
                        "response": "error",
                        "error": f"Streamer in state {state_return[0]} can not be started.",
                        "state": state_return,
                    }
                ),
                200,
            )

    @app.route("/stop", methods=["POST"])
    def stop_streamer():
        """POST request to stop the stream repeater object.

        Returns:
            HTTP response with status of the request and the state of the stream repeater object.
        """
        if app.config["state"] == State.RUNNING:
            try:
                _logger.debug(f"Service Rest Stream Repeater: stopping...")
                repeater.stop()
                app.config["state"] = State.STOPPED
                app.config['valid_writer_config'] = False
                app.config['std_det_output'] = False
                app.config['valid_config'] = False
            except BaseException as err:
                app.config["state"] = State.ERROR
                return make_response(
                    jsonify(
                        {
                            "response": "error",
                            "error": f"Unexpected {err=}, {type(err)=}",
                        }
                    ),
                    200,
                )
            state_return = (app.config["state"].name, app.config["state"].value)
            return make_response(
                jsonify({"response": "success", "state": state_return}),
                200,
            )
        else:
            return make_response(
                jsonify(
                    {
                        "response": "error",
                        "state": (app.config["state"].name, app.config["state"].value),
                        "error": "Streamer is not running.",
                    }
                ),
                200,
            )

    app.run(host="0.0.0.0", port=port, threaded=True, debug=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rest Stream Repeater")

    parser.add_argument("--port", default=8888, help="Port of the repeater stream.")
    parser.add_argument(
        "--log_level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Log level to use.",
    )
    parser.add_argument(
        "--config_file",
        default="repstream_config.json",
        help="Default config file.",
    )

    args = parser.parse_args()

    _logger.setLevel(args.log_level)

    _logger.info(f"Service Rest Stream Repeater running on port {args.port}.")

    start_rest_api(port=args.port, config_file=args.config_file)

    _logger.info(f"Service Rest Stream Repeater stopping.")
