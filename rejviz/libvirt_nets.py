# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License. You may
# obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

import logging
from xml.etree import ElementTree

import libvirt

LOG = logging.getLogger(__file__)


def get_libvirt_networks():
    conn = libvirt.openReadOnly()
    if not conn:
        raise RuntimeError('Could not connect to libvirt.')

    networks = [_fetch_network_data(n) for n in conn.listAllNetworks()]
    conn.close()
    return networks


def _fetch_network_data(network):
    network_data = {'name': network.name()}

    root = ElementTree.fromstring(network.XMLDesc())
    network_data['dhcp'] = root.find('./ip/dhcp') is not None
    network_data['netmask'] = root.find('./ip').attrib['netmask']
    network_data['network'] = _gateway_ipaddr_to_network(
        root.find('./ip').attrib['address'])

    return network_data


def _gateway_ipaddr_to_network(ipaddr):
    octets = ipaddr.split('.')
    # smarty pants
    octets[3] = str(int(octets[3]) - 1)
    return '.'.join(octets)
