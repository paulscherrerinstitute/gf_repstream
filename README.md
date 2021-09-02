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
    usage: gf_repstream [-h] [-v] [--in-address PROTOCOL://HOST:PORT] [--out-address PROTOCOL://HOST:PORT] [--in-connection-mode {connect,bind}]
                        [--out-connection-mode {connect,bind}] [--io-threads IO_THREADS] [--buffer-size BUFFER_SIZE]

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit
    --in-address PROTOCOL://HOST:PORT
                            an address string for zmq socket (default: tcp://xbl-daq-23:9990)
    --out-address PROTOCOL://HOST:PORT
                            an address string for zmq socket (default: tcp://*:9610)
    --in-connection-mode {connect,bind}
                            whether to bind a socket to an address or connect to a remote socket with an address (default: connect)
    --out-connection-mode {connect,bind}
                            whether to bind a socket to an address or connect to a remote socket with an address (default: bind)
    --io-threads IO_THREADS
                            the size of the zmq thread pool to handle I/O operations (default: 1)
    --buffer-size BUFFER_SIZE
                            a number of last received zmq messages to keep in memory (default: 2000)
```

<!-- LICENSE -->
## License

See `LICENSE` for more information.


## Authors

* [Leonardo Hax Damiani](leonardo.hax@psi.ch)
* [Andrej Babic](andrej.babic@psi.ch)
* [Christian Schlepuetz](christian.schlepuetz@psi.ch)
* [Federica Marone](federica.marine@psi.ch)





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
