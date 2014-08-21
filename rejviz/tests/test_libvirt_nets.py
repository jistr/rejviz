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

import mock

from rejviz import libvirt_nets
import rejviz.tests.utils as tutils


NETWORK_XMLDESC = """
<network>
  <name>default</name>
  <uuid>d2f553ca-f9fe-49cb-996d-934a69fc02da</uuid>
  <forward mode='nat'>
    <nat>
      <port start='1024' end='65535'/>
    </nat>
  </forward>
  <bridge name='virbr0' stp='on' delay='0'/>
  <mac address='52:54:00:f7:fc:83'/>
  <ip address='192.168.122.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254'/>
    </dhcp>
  </ip>
</network>
"""


class LibvirtNetsTest(tutils.TestCase):

    @mock.patch('libvirt.openReadOnly')
    @mock.patch('rejviz.libvirt_nets._fetch_network_data')
    def test_get_libvirt_networks(self, _fetch_network_data, openReadOnly):
        conn = openReadOnly.return_value
        conn.listAllNetworks.return_value = ['net1', 'net2']

        networks = libvirt_nets.get_libvirt_networks()

        self.assertEqual([_fetch_network_data.return_value,
                          _fetch_network_data.return_value],
                         networks)
        openReadOnly.assertCalledWith()
        conn.listAllNetworks.assertCalledWith()
        _fetch_network_data.assertCalledWith('net1')
        _fetch_network_data.assertCalledWith('net2')
        conn.close.assertCalledWith()

    def test_fetch_network_data(self):
        network_object = mock.MagicMock()
        network_object.name.return_value = 'default'
        network_object.XMLDesc.return_value = NETWORK_XMLDESC

        network = libvirt_nets._fetch_network_data(network_object)
        self.assertEqual('default', network['name'])
        self.assertEqual(True, network['dhcp'])
        self.assertEqual('192.168.122.0', network['network'])
        self.assertEqual('255.255.255.0', network['netmask'])

    def test_gateway_ipaddr_to_network(self):
        # for 192.168.122.0/24
        self.assertEqual(
            '192.168.122.0',
            libvirt_nets._gateway_ipaddr_to_network('192.168.122.1'))
        # for 192.168.123.192/26
        self.assertEqual(
            '192.168.123.192',
            libvirt_nets._gateway_ipaddr_to_network('192.168.123.193'))
