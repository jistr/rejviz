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
from testtools import matchers

from rejviz import nic
import rejviz.tests.utils as tutils


class NicTest(tutils.TestCase):

    @mock.patch('rejviz.nic._nic_values_to_args',
                return_value=['--upload', '/one:/two'])
    def test_process_args_with_spaces(self, nic_values_to_args):
        # prepare
        args = [
            '--size', '10G',
            '--nic', 'ipaddr=192.168.122.10;hwaddr=ab:cd:ef:gh:ij',
            '--install', 'wget',
        ]

        # run
        final_args = nic.process_args(args, '/tmp/dir')

        # verify
        self.assertEqual([
            '--size', '10G',
            '--upload', '/one:/two',
            '--install', 'wget',
        ], final_args)
        nic_values_to_args.assert_called_with(
            'ipaddr=192.168.122.10;hwaddr=ab:cd:ef:gh:ij', '/tmp/dir')

    @mock.patch('rejviz.nic._nic_values_to_args',
                return_value=['--upload', '/one:/two'])
    def test_process_args_with_equals(self, nic_values_to_args):
        # prepare
        args = [
            '--size=10G',
            '--nic=ipaddr=192.168.122.10;hwaddr=ab:cd:ef:gh:ij',
            '--install=wget',
        ]

        # run
        final_args = nic.process_args(args, '/tmp/dir')

        # verify
        self.assertEqual([
            '--size=10G',
            '--upload', '/one:/two',
            '--install=wget',
        ], final_args)
        nic_values_to_args.assert_called_with(
            'ipaddr=192.168.122.10;hwaddr=ab:cd:ef:gh:ij', '/tmp/dir')

    @mock.patch('rejviz.nic._ensure_nic_vars', return_value={'name': 'eth0'})
    @mock.patch('rejviz.nic._render_nic_template', return_value='rendered')
    @mock.patch('rejviz.nic.open', new_callable=mock.mock_open, create=True)
    @mock.patch('os.makedirs')
    def test_nic_values_to_args(self, makedirs, open_,
                                render_nic_template, ensure_nic_vars):
        # run
        args = nic._nic_values_to_args('name=eth0', '/tmp/rejviz-builder-123')

        # verify
        ensure_nic_vars.assert_called_with({'name': 'eth0'})
        render_nic_template.assert_called_with({'name': 'eth0'})
        makedirs.assert_called_with(
            '/tmp/rejviz-builder-123/etc/sysconfig/network-scripts', 0o700)
        open_.assert_called_with(
            '/tmp/rejviz-builder-123/etc/sysconfig/network-scripts/ifcfg-eth0',
            'w')
        open_().write.assert_called_with('rendered')
        self.assertEqual(
            [
                '--upload',
                ("/tmp/rejviz-builder-123/etc/sysconfig/network-scripts/"
                 "ifcfg-eth0:/etc/sysconfig/network-scripts/ifcfg-eth0"),
            ],
            args)

    def test_render_nic_template(self):
        nic_vars = {
            'name': 'eth0',
            'hwaddr': '12:34:56:ab:cd:ef',
            'bootproto': 'static',
            'ipaddr': '192.168.122.10',
            'network': '192.168.122.0',
            'netmask': '255.255.255.0',
            'broadcast': '192.168.122.255',
            'gateway': '192.168.122.1',
            'dns1': '192.168.122.1',
        }
        expected = """\
        HWADDR=12:34:56:ab:cd:ef
        TYPE=Ethernet
        BOOTPROTO=static
        DEFROUTE=yes
        PEERDNS=yes
        PEERROUTES=yes
        IPADDR=192.168.122.10
        NETWORK=192.168.122.0
        NETMASK=255.255.255.0
        BROADCAST=192.168.122.255
        GATEWAY=192.168.122.1
        DNS1=192.168.122.1

        IPV4_FAILURE_FATAL=no
        IPV6INIT=yes
        IPV6_AUTOCONF=yes
        IPV6_DEFROUTE=yes
        IPV6_PEERDNS=yes
        IPV6_PEERROUTES=yes
        IPV6_FAILURE_FATAL=no
        NAME=eth0
        ONBOOT=yes""".replace('        ', '')
        self.assertEqual(expected, nic._render_nic_template(nic_vars))

    def test_ensure_nic_vars_no_name(self):
        nic_vars = {
            'hwaddr': '12:34:56:ab:cd:ef',
            'bootproto': 'dhcp',
            'ipaddr': '192.168.122.10',
        }
        self.assertRaises(ValueError, nic._ensure_nic_vars, nic_vars)

    def test_ensure_nic_vars_static_no_ip(self):
        nic_vars = {
            'name': 'eth0',
            'hwaddr': '12:34:56:ab:cd:ef',
            'bootproto': 'static',
        }
        self.assertRaises(ValueError, nic._ensure_nic_vars, nic_vars)

    def test_ensure_nic_vars_minimal(self):
        nic_vars = {
            'name': 'eth0',
        }
        ensured = nic._ensure_nic_vars(nic_vars)
        self.assertEqual(3, len(ensured))
        self.assertEqual('eth0', ensured['name'])
        self.assertEqual('dhcp', ensured['bootproto'])
        self.assertThat(
            ensured['hwaddr'],
            matchers.MatchesRegex(
                '^52:54:00:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$'))

    def test_ensure_nic_vars_static_minimal(self):
        nic_vars = {
            'name': 'eth0',
            'hwaddr': '12:34:56:ab:cd:ef',
            'ipaddr': '192.168.122.10',
        }
        expected = {
            'name': 'eth0',
            'hwaddr': '12:34:56:ab:cd:ef',
            'bootproto': 'static',
            'ipaddr': '192.168.122.10',
            'network': '192.168.122.0',
            'netmask': '255.255.255.0',
            'broadcast': '192.168.122.255',
        }
        self.assertEqual(expected, nic._ensure_nic_vars(nic_vars))

    def test_ensure_nic_vars_dhcp(self):
        nic_vars = {
            'name': 'eth0',
            'hwaddr': '12:34:56:ab:cd:ef',
            'bootproto': 'dhcp',
            'broadcast': '192.168.122.255',
        }
        expected = {
            'name': 'eth0',
            'hwaddr': '12:34:56:ab:cd:ef',
            'bootproto': 'dhcp',
        }
        self.assertEqual(expected, nic._ensure_nic_vars(nic_vars))

    def test_generate_mac_address(self):
        # testing randomness is bad, but in this case the probability
        # of non-deterministic failure is extremely low
        self.assertThat(
            nic._generate_mac_address(),
            matchers.MatchesRegex(
                '^52:54:00:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$'))
