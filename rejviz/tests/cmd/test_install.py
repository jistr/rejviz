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

from rejviz.cmd import install
import rejviz.tests.utils as tutils


class InstallTest(tutils.TestCase):

    @mock.patch('subprocess.call')
    @mock.patch('sys.argv', new=['rejviz-install', '--one', '--two'])
    def test_main(self, call):
        install.main()

        call.assert_called_with(['virt-install', '--one', '--two'])
