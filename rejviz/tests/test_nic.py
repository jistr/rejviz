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

import rejviz.nic as nic
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
            '192.168.122.10;hwaddr=ab:cd:ef:gh:ij', '/tmp/dir')

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
            '192.168.122.10;hwaddr=ab:cd:ef:gh:ij', '/tmp/dir')
