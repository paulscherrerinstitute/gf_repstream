from flask import Flask, request, jsonify, make_response
from flask_session import Session

import argparse
import logging
import pkg_resources
from enum import Enum

from cli import SRepeater

__author__ = 'Leonardo Hax Damiani'
__date_created__ = '2020-08-20'
__credits__ = 'Christian M. Schlepuetz'
__copyright__ = 'Copyright (c) 2021, Paul Scherrer Institut'
__docformat__ = 'restructuredtext en'


class State(Enum):
    CONFIGURED = 0
    RUNNING = 1
    ERROR = 2
    STOPPED = 3


_logger = logging.getLogger("RestStreamRepeater")

app = Flask('RestStreamRepeater')
app.config['state'] = None
Session(app)


def start_rest_api(port, config_file):
    """Function that starts the rest server and listen to the commands that control the stream repeater service.

    Args:
        port (int): Port that the stream repeater REST api will listen to
        config_file (str): Path to stream repeater config file

    """
    # FIXME: static file should be loaded from the package via pkg_resources prior to deployment
    # repeater = SRepeater(config_file='./static/repstream_config.json')
    repeater = SRepeater(config_file='./static/fake_stream.json')
    app.config['state'] = State.CONFIGURED

    @app.route("/get_config", methods=['GET'])
    def get_config():
        """Gets the configuration from the stream repeater object.

        Returns:
            HTTP response with status of the request, configuration and state of the stream repeater.
        """
        
        try:
            config = repeater.get_config()
            state_return = (
                app.config['state'].name,
                app.config['state'].value)
            _logger.debug(f'Service Rest Stream Repeater: {state_return}')
        except BaseException as err:
            return make_response(jsonify(
                {'response': 'error', 'error': f"Unexpected {err=}, {type(err)=}"}), 200,)
        return make_response(jsonify({'response': 'success',
                                      'state': state_return,
                                      'config': config}), 200,)

    @app.route("/get_state", methods=['GET'])
    def get_state():
        """GET request to load the state from the stream repeater object.

        Returns:
            HTTP response with status of the request and state of the stream repeater object.
        """
        try:
            state_return = (
                app.config['state'].name,
                app.config['state'].value)
            _logger.debug(f'Service Rest Stream Repeater: {state_return}')
        except BaseException as err:
            app.config['state'] = State.ERROR
            return make_response(jsonify(
                {'response': 'error', 'error': f"Unexpected {err=}, {type(err)=}"}), 200,)
        return make_response(jsonify({'response': 'success',
                                      'state': state_return}), 200,)

    @app.route("/set_config", methods=['POST'])
    def set_config():
        """POST request to set a new configuration into the stream repeater object.

        Returns:
            HTTP response with status of the request and the state of the stream repeater object.
        """
        config = request.json
        try:
            new_config_file = config['config_file']
            repeater.set_config_file(new_config_file)
            app.config['state'] = State.CONFIGURED
            _logger.debug(f'Service Rest Stream Repeater: new config file {new_config_file}')
        except BaseException as err:
            app.config['state'] = State.ERROR
            return make_response(jsonify(
                {'response': 'error', 'error': f"Unexpected {err=}, {type(err)=}"}), 200,)
        return make_response(jsonify({'response': 'success', 'state': (
            app.config['state'].name, app.config['state'].value)}), 200,)

    @app.route("/start", methods=['POST'])
    def start_streamer():
        """POST request to start a new stream using the configured stream repeater object.

        Returns:
            HTTP response with status of the request and the state of the stream repeater object.
        """
        if app.config['state'] == State.CONFIGURED:
            try:
                _logger.debug(f'Service Rest Stream Repeater: starting...')
                repeater.start()
                app.config['state'] = State.RUNNING
            except BaseException as err:
                app.config['state'] = State.ERROR
                return make_response(jsonify(
                    {'response': 'error', 'error': f"Unexpected {err=}, {type(err)=}"}), 200,)
            state_return = (
                app.config['state'].name,
                app.config['state'].value)
            return make_response(
                jsonify({'response': 'success', 'state': state_return}), 200,)
        else:
            state_return = (
                app.config['state'].name,
                app.config['state'].value)
            return make_response(jsonify(
                {'response': 'error', 'error': 'Streamer is not configured.',
                    'state': state_return}), 200,)

    @app.route("/stop", methods=['POST'])
    def stop_streamer():
        """POST request to stop the stream repeater object.

        Returns:
            HTTP response with status of the request and the state of the stream repeater object.
        """
        if app.config['state'] == State.RUNNING:
            try:
                _logger.debug(f'Service Rest Stream Repeater: stopping...')
                repeater.stop()
                app.config['state'] = State.STOPPED
            except BaseException as err:
                app.config['state'] = State.ERROR
                return make_response(jsonify(
                    {'response': 'error', 'error': f"Unexpected {err=}, {type(err)=}"}), 200,)
            state_return = (
                app.config['state'].name,
                app.config['state'].value)
            return make_response(jsonify({'response': 'success', 'state': state_return}), 200,)
        else:
            return make_response(jsonify({
                        'response': 'error',
                        'state': (
                            app.config['state'].name,
                            app.config['state'].value),
                        'error': 'Streamer is not running.'}),200,)

    app.run(host='127.0.0.1', port=port, threaded=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rest Stream Repeater')

    parser.add_argument("--port", default=8888,
                        help="Port of the repeater stream.")
    parser.add_argument("--log_level", default="INFO",
                        choices=[
                            'CRITICAL',
                            'ERROR',
                            'WARNING',
                            'INFO',
                            'DEBUG'],
                        help="Log level to use.")
    parser.add_argument(
        "--config-file",
        default='./static/repstream_config.json',
        help="Default config file.")

    args = parser.parse_args()

    _logger.setLevel(args.log_level)

    _logger.info(f'Service Rest Stream Repeater running on port {args.port}.')

    start_rest_api(port=args.port, config_file=args.config_file)

    _logger.info(f'Service Rest Stream Repeater stopping.')
