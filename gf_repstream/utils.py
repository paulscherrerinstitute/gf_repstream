#!/usr/bin/env python
import ipaddress
import re
import zmq 

def validate_zmq_mode(zmq_mode):
    if zmq_mode.upper() in ['PULL', 'PUB']:
        return True
    return False


def validate_network_address(network_address, protocol='tcp'):
    """
    Verify if a network address is valid.
    In the context of this method, a network addres must fulfill the following
    criteria to be valid:
    * It must start with a protocol specifier of the following form:
      "<PROT>://", where <PROT> can be any of the usual protocols.
      E.g.: "http://"
    * The protocol specifier is followed by a valid IP v4 address or a  host
      name (a host name must contain at least one alpha character)
    * The network address is terminated with a 4-5 digit port number preceeded
      by a colon. E.g.: ":8080"
    If all of these critera are met, the passed network address is returned
    again, otherwise the method returns None
    Parameters
    ----------
    network_address : str
        The network address to be verified.
    protocol : str, optional
        The network protocol that should be ascertained during the validity
        check. (default = 'tcp')
    Returns
    -------
    net_addr : str or None
        The validated network address. If the validation failed, None is
        returned.
    """
    # localhost
    if 'localhost' in network_address:
    	return True
    # ip v4 pattern with no leading zeros and values up to 255
    ip_pattern = ("(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
                  "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
    # hostname pattern requiring at least one (non-numeric AND non-period)-
    # character (to distinguish it from an ip address)
    hostname_pattern = "[\\w.\\-]*[^0-9.][\\w.\\-]*"
    # ports with 4 or 5 digits. No check is done for max port number of 65535
    port_pattern = ":[0-9]{4,5}"
    # protocol pattern end with "://". e.g.: "https://""
    protocol_pattern = "%s:[/]{2}" % protocol

    # check if address is given with an IP address
    ip_find_pattern = "(?<={}){}(?={})".format(
        protocol_pattern, ip_pattern, port_pattern)
    ip = re.findall(ip_find_pattern, network_address)
    if ip:
        try:
            ip = validate_ip_address(ip[0])
        except Exception as e:
            raise RuntimeError(e)
        connection_pattern = protocol_pattern + ip_pattern + port_pattern
        if bool(re.match(connection_pattern, network_address)):
            return network_address

def valid_writer_config(writer_dict):
    mandatory_keys = ["output_file", "run_id","n_images", "detector_name"]
    for mandatory_key in mandatory_keys:
        if mandatory_key not in writer_dict:
            return False
    return True

def validate_ip_address(ip_address):
    """
    Check whether the supplied string is a valid IP address.
    The method will simply raise the exception from the ipaddress module if the
    address is not valid.
    Parameters
    ----------
    ip_address : str
        The string representation of the IP address.
    Returns
    -------
    ip_address : str
        The validated IP address in string representation.
    """

    if not type(ip_address) is type(u""):
        ip_address = ip_address.decode()
    ip = ipaddress.ip_address(ip_address)
    return str(ip)
