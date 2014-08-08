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

import rejviz.tests.utils as tutils
from rejviz import tmp


class TmpTest(tutils.TestCase):

    @mock.patch('rejviz.tmp.path.exists', return_value=False)
    @mock.patch('rejviz.tmp.os.mkdir')
    def test_create_dir(self, mkdir, exists):
        tmp_dir = tmp.create_dir()

        mkdir.assert_called_with(tmp_dir, 0o700)
        self.assertThat(tmp_dir,
                        matchers.MatchesRegex('^/tmp/rejviz-builder-\\d+$'))

    @mock.patch('rejviz.tmp.shutil.rmtree')
    def test_remove_dir_ok(self, rmtree):
        tmp.remove_dir('/tmp/rejviz-builder-123')
        rmtree.assert_called_with('/tmp/rejviz-builder-123')

    @mock.patch('rejviz.tmp.shutil.rmtree')
    def test_remove_dir_bad_prefix(self, rmtree):
        self.assertRaises(ValueError, tmp.remove_dir, '/tmp/rejviz-123')
        self.assertEqual([], rmtree.mock_calls)
