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

import subprocess

import mock

from rejviz import nic_mappings
import rejviz.tests.utils as tutils


NICS_SCRIPT = u'''aug-init / 0
echo @name
echo eth0
echo @type
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth0/TYPE
echo @hwaddr
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth0/HWADDR
echo @bootproto
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth0/BOOTPROTO
echo @network
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth0/NETWORK
echo @netmask
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth0/NETMASK
echo @-----
echo @name
echo eth1
echo @type
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth1/TYPE
echo @hwaddr
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth1/HWADDR
echo @bootproto
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth1/BOOTPROTO
echo @network
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth1/NETWORK
echo @netmask
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-eth1/NETMASK
echo @-----
echo @name
echo lo
echo @type
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-lo/TYPE
echo @hwaddr
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-lo/HWADDR
echo @bootproto
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-lo/BOOTPROTO
echo @network
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-lo/NETWORK
echo @netmask
-aug-get /files/etc/sysconfig/network-scripts/ifcfg-lo/NETMASK
echo @-----
'''


NICS_OUTPUT = '''@name
eth0
@type
Ethernet
@hwaddr
52:54:00:12:34:56
@bootproto
dhcp
@network
@netmask
@-----
@name
eth1
@type
Ethernet
@hwaddr
52:54:00:12:34:78
@bootproto
static
@network
192.168.123.0
@netmask
255.255.255.0
@-----
@name
loopback
@type
@hwaddr
@bootproto
@network
127.0.0.0
@netmask
255.0.0.0
@-----
'''


class NicMappingTest(tutils.TestCase):

    def test_has_nic_mapping_args(self):
        self.assertTrue(nic_mappings._has_nic_mapping_args(
            ['--disk', '/image', '--auto-nic-mappings']))
        self.assertTrue(nic_mappings._has_nic_mapping_args(
            ['--disk', '/image', '--nic-mappings', 'eth0=net1']))
        self.assertFalse(nic_mappings._has_nic_mapping_args(
            ['--disk', '/image']))

    @mock.patch('subprocess.Popen')
    @mock.patch('rejviz.nic_mappings._get_nic_names_from_image')
    def test_fetch_nics_from_image(self, get_nic_names, popen):
        # setup
        popen.return_value.communicate.return_value = (
            NICS_OUTPUT, 'stderr contents')
        get_nic_names.return_value = ['eth0', 'eth1', 'lo']

        # test
        nics = nic_mappings._fetch_nics_from_image(['--disk', '/image'])
        popen.assert_called_with(
            ['guestfish', '-i', '--ro', '-a', '/image'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        popen.return_value.communicate.assert_called_with(NICS_SCRIPT)
        get_nic_names.assert_called_with(['-a', '/image'])
        self.assertEqual(2, len(nics))
        self.assertEqual(['eth0', 'eth1'], [n['name'] for n in nics])

    @mock.patch('subprocess.check_output')
    def test_get_nic_names_from_image(self, check_output):
        check_output.return_value = (
            'ifcfg-eth0\n'
            'ifcfg-eth1\n'
            'ifdown-eth0\n'
            'ifdown-eth1\n'
            'ifup-eth0\n'
            'ifup-eth1\n')

        self.assertEqual(
            ['eth0', 'eth1'],
            nic_mappings._get_nic_names_from_image(['-a', '/image']))
        check_output.assert_called_with(
            ['virt-ls', '-a', '/image',
             '/etc/sysconfig/network-scripts'])

    def test_parse_nics_output(self):
        self.assertEqual(
            [
                {'name': 'eth0', 'type': 'Ethernet',
                 'hwaddr': '52:54:00:12:34:56', 'bootproto': 'dhcp',
                 'network': None, 'netmask': None},
                {'name': 'eth1', 'type': 'Ethernet',
                 'hwaddr': '52:54:00:12:34:78', 'bootproto': 'static',
                 'network': '192.168.123.0', 'netmask': '255.255.255.0'},
                {'name': 'loopback', 'type': None,
                 'hwaddr': None, 'bootproto': None,
                 'network': '127.0.0.0', 'netmask': '255.0.0.0'},
            ],
            nic_mappings._parse_nics_output(NICS_OUTPUT)
        )

    def test_filter_ethernet_nics(self):
        self.assertEqual(
            [
                {'name': 'eth0', 'type': 'Ethernet',
                 'hwaddr': '52:54:00:12:34:56', 'bootproto': 'dhcp',
                 'network': None, 'netmask': None},
                {'name': 'eth1', 'type': 'Ethernet',
                 'hwaddr': '52:54:00:12:34:78', 'bootproto': 'static',
                 'network': '192.168.123.0', 'netmask': '255.255.255.0'},
            ],
            nic_mappings._filter_ethernet_nics([
                {'name': 'eth0', 'type': 'Ethernet',
                 'hwaddr': '52:54:00:12:34:56', 'bootproto': 'dhcp',
                 'network': None, 'netmask': None},
                {'name': 'eth1', 'type': 'Ethernet',
                 'hwaddr': '52:54:00:12:34:78', 'bootproto': 'static',
                 'network': '192.168.123.0', 'netmask': '255.255.255.0'},
                {'name': 'loopback', 'type': None,
                 'hwaddr': None, 'bootproto': None,
                 'network': '127.0.0.0', 'netmask': '255.0.0.0'},
            ]),
        )
