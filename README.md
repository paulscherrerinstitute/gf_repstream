<!-- ABOUT THE PROJECT -->
## GF_REPSTREAM
This is a tool to receive an incoming ZMQ stream, treat it (optional), and stream it to external components. This is developed for usage with Gigafrost camera stream at the TOMCAT beamline at Paul Scherrer Institute.

The fake gigafrost stream generator was done inspired/using https://github.com/paulscherrerinstitute/mflow

<!-- USAGE EXAMPLES -->
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
```

### Fake stream

From file:
```bash
    python -m gf_repstream.test.fake_stream-a <tcp://<address>:<port> -f <path_to_data.raw> -m <mode>
```

The data can be found in the folder ```test/test_data``` and the stream will iterate over the existing data until ctrl+C is pressed, terminating the stream.

### Consumer
```bash
     python -m gf_repstream.test.consume_stream -a tcp://localhost:9611 -m SUB 
```

If header format is the protocol TestMetadata, one can use ```-f TestMetadata``` on the consumer side.


## Anaconda 

### Building the package

```bash
    conda build conda-recipe
```

### Uploading the package

```bash
    anaconda upload <path_to.tar.bz2_file>
```

<!--### Installing the package

```bash
    conda install -c paulscherrerinstitute gf_repstream
```-->


<!-- LICENSE -->
## License

See `LICENSE` for more information.


## Authors

* Leonardo Hax Damiani (leonardo.hax@psi.ch)
