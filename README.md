<!-- ABOUT THE PROJECT -->
## About The Project
This is a tool to receive an incoming ZMQ stream, treat it (optional), and stream it to external components. This is developed for usage with Gigafrost camera stream at the TOMCAT beamline at Paul Scherrer Institute.


### Built With

* [PyZMQ](https://pyzmq.readthedocs.io/en/latest/)


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

### Installation

<!-- USAGE EXAMPLES -->
## Usage
```bash
    usage: gf_repstream [-h] [-v] [--in-address PROTOCOL://HOST:PORT] [--out-init-port PROTOCOL://HOST:PORT] [--io-threads IO_THREADS] [--buffer-size BUFFER_SIZE] [--n-output-streams N_OUTPUT_STREAMS]
                        [--send-every-nth SEND_EVERY_NTH [SEND_EVERY_NTH ...]]

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show version number and exit
    --in-address PROTOCOL://HOST:PORT
                            an address string for zmq socket (default: tcp://xbl-daq-23:9990)
    --out-init-port PROTOCOL://HOST:PORT
                            the initial port for the output streams (increased by 1 for every other stream) (default: 9610)
    --io-threads IO_THREADS
                            the size of the zmq thread pool to handle I/O operations (default: 1)
    --buffer-size BUFFER_SIZE
                            a number of last received zmq messages to keep in memory (default: 100)
    --n-output-streams N_OUTPUT_STREAMS
                            number of output streams to be generated (default: 0)
    --send-every-nth SEND_EVERY_NTH [SEND_EVERY_NTH ...]
                            list containing the frequency of each output stream to be generated (default: None)
```

example:

```bash
    python -m gf_repstream.cli --in-address tcp://localhost:9609 --out-init-port 9610 --n-outputs 3 --send-every-nth 1 2 10
```

### Fake stream

```bash
    python -m gf_repstream.test.fake_stream tcp://*:9609
```

### Consumer
```bash
     python -m gf_repstream.test.consume_stream tcp://localhost:9611 SUB
```

<!-- LICENSE -->
## License

See `LICENSE` for more information.


## Authors

* Leonardo Hax Damiani (leonardo.hax@psi.ch)
* Christian Schlepuetz (christian.schlepuetz@psi.ch)








<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo.svg?style=for-the-badge
[contributors-url]: https://github.com/github_username/repo_name/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo.svg?style=for-the-badge
[forks-url]: https://github.com/github_username/repo_name/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo.svg?style=for-the-badge
[stars-url]: https://github.com/github_username/repo_name/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/repo.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/repo_name/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo.svg?style=for-the-badge
[license-url]: https://github.com/github_username/repo_name/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/github_username
