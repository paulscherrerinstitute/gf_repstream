[![Conda](https://img.shields.io/conda/pn/paulscherrerinstitute/gf_repstream?color=success)](https://anaconda.org/paulscherrerinstitute/gf_repstream)  [![GitHub](https://img.shields.io/github/license/paulscherrerinstitute/gf_repstream)](https://github.com/paulscherrerinstitute/gf_repstream/blob/master/LICENSE) ![GitHub Release Date](https://img.shields.io/github/release-date/paulscherrerinstitute/gf_repstream) ![conda_publish](https://github.com/paulscherrerinstitute/gf_repstream/workflows/conda_publish/badge.svg)

<!-- ABOUT THE PROJECT -->
## ZMQ_REPSTREAM
This is a tool to receive an incoming ZMQ stream, treat it (optional), and stream it to multiple clients/external components. It works controlled via a REST api that allows the user to configure and control it.

-----
** NOTE ** 

A optional mode allows one to prepare a stream directed to the [std-det-writer](https://github.com/paulscherrerinstitute/sf_daq_buffer/tree/eiger/std-det-writer) for saving the incoming stream, it is necessary to also configure the writer details (outputfile, number of images, etc...)

The fake gigafrost stream generator was done inspired in [mflow](https://github.com/paulscherrerinstitute/mflow)

The streamer has 4 states: INITIALIZED, RUNNING, ERROR, STOPPED. 

## REST SERVER

To start the rest server and prepare the streamer object, run app.py
```bash
python app.py
```

## Endpoints Overview

- ``/initialize`` (POST): prepares the streamer object with the defined configuration.
- ``/get_status`` (GET): gets the current configuration and state of the streamer object
- ``/get_state`` (GET): gets the state of the streamer object
- ``/set_config_from_dict`` (POST): sets the configuration of the streamer object with via a json.
    - The dictionary can have one or multiple the following keys: in_address, in_zmq_mode, io_threads, buffer_size, n_output_streams, send_output_mode, send_output_param, stream_ports, zmq_modes, mode_metadata, config_file, frame_block
- ``/set_config_from_file`` (POST): sets the configuration of the streamer object by providing a path to a config file.
- ``/set_writer_config`` (POST): Sets the writer configuration in the streamer object via a json. 
    - The json must have the following keys: output_file, run_id, n_images, detector_name
- ``/start`` (POST): Start the streamer object.
- ``/stop`` (POST): Stop the streamer object.

## Configuration parameters overview
- in_address: Incoming ZMQ address. Defaults to "tcp://xbl-daq-23:9990".
- in_zmq_mode: Incoming ZMQ mode. Defaults to PULL.
- io_threads: ZMQ IO threads. Defaults to 1. 
- buffer_size:  ZMQ buffer size. Defaults to 5000.
- n_output_streams: Number of output streams. Defaults to None. 
- send_output_mode: List containing the ZMQ mode of the generated output streams. Defaults to None.
- send_output_param: List containing the output streams configuration parameter. Defaults to None.
- stream_ports: List containing the output port of the output streams.
- zmq_modes: List containing the ZMQ connection modes of the output streams.
- config_file: Path to the config file. Defaults to None.
- frame_block:Total number of frames to create a block. Defaults to 15

## Writer parameters overview
- ``output_file``: name of the output file
- ``run_id``: id of the run (or acquisition)
- ``n_images``: total number of images that will be written to the output file.
- ``detector_name``: name of the detector/camera.

### send_output_mode and send_output_param
- ``send_every_nth``: sends every nth frame (n is defined by send_output_param)
- ``send_every_sec``: sends a frame every n seconds (n is defined by send_output_param)
- ``send_every_nth_frame``: sends Y frames every N frames (Y is defined by send_output_param and N is defined by the parameter frame_block)
    - Note that frame_block is fixed and can not be adjusted if multiple streams are using the ``send_every_nth_frame`` mode.
- ``strides``: sends n frames and skip the next n frames (n is defined by send_output_param)


<!-- 
<!-- USAGE EXAMPLES 
## Usage
```bash
    usage: gf_repstream [-h] [-v] [--in-address PROTOCOL://HOST:PORT] [--in-zmq-mode IN_ZMQ_MODE] [--out-init-port OUT_INIT_PORT] [--io-threads IO_THREADS] [--buffer-size BUFFER_SIZE]
                    [--n-output-streams N_OUTPUT_STREAMS] [--send-every-nth SEND_EVERY_NTH [SEND_EVERY_NTH ...]] [--mode-metadata MODE_METADATA] [--config-file CONFIG_FILE]

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show programs version number and exit
    --in-address PROTOCOL://HOST:PORT
                            an address string for zmq socket (default: tcp://xbl-daq-23:9990)
    --in-zmq-mode IN_ZMQ_MODE
                            Input stream zmq mode (SUB or PULL) (default: PULL)
    --out-init-port OUT_INIT_PORT
                            the initial port for the output streams (increased by 1 for every other stream) (default: 9610)
    --io-threads IO_THREADS
                            the size of the zmq thread pool to handle I/O operations (default: 1)
    --buffer-size BUFFER_SIZE
                            a number of last received zmq messages to keep in memory (default: 100)
    --n-output-streams N_OUTPUT_STREAMS
                            number of output streams to be generated (default: 0)
    --send-every-nth SEND_EVERY_NTH [SEND_EVERY_NTH ...]
                            list containing the frequency of each output stream to be generated (default: None)
    --mode-metadata MODE_METADATA
                            Incoming header data. (default: file)
    --config-file CONFIG_FILE
                            A gf_repstream config file (default: None)
```

usage example via config file:
```bash
    python -m gf_repstream.cli --config-file ./gf_repstream/test/repstream_config.json
```

usage example via command line:
```bash
    python -m gf_repstream.cli --in-address tcp://localhost:9609 --out-init-port 9610 --n-outputs 3 --send-every-nth 1 2 10
``` -->

### Fake stream

From file:
```bash
    python -m gf_repstream.test.fake_stream -a <tcp://<address>:<port> -f <path_to_data.raw> -m <mode>
```

The data can be found in the folder ```test/test_data``` and the stream will iterate over the existing data until ctrl+C is pressed, terminating the stream.

### Consumer
```bash
     python -m gf_repstream.test.consume_stream -a tcp://localhost:9611 -m SUB 
```

If header format is the protocol TestMetadata, one can use ```-f TestMetadata``` on the consumer side.


## Anaconda 

### Building the package

From the home directory, run:

```bash
    conda build conda-recipe
```

### Uploading the package

```bash
    anaconda upload <path_to.tar.bz2_file>
```

### Installing the package

```bash
    conda install -c paulscherrerinstitute gf_repstream
```


<!-- LICENSE -->
## License

See `LICENSE` for more information.


## Authors

* Leonardo Hax Damiani (leonardo.hax@psi.ch)
* Christian M. Schlepütz (christian.schlepuetz@psi.ch)