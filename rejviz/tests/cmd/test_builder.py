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

import rejviz.cmd.builder as builder


@mock.patch('rejviz.cmd.builder.tmp')
@mock.patch('rejviz.cmd.subprocess')
@mock.patch('rejviz.cmd.sys.argv', new=['--one', '--two'])
def test_main(argv, subprocess, tmp):
    # prepare
    tmp.create_dir.return_value = '/tmp/abc'

    # run
    builder.main()

    # verify
    tmp.create_dir.assert_called_with()
    subprocess.call.assert_called_with(['virt-builder', '--one', '--two'])
    tmp.remove_dir.assert_called_with('/tmp/abc')
