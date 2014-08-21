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

import rejviz.tests.utils as tutils
from rejviz import utils


class UtilsTest(tutils.TestCase):

    def test_parse_keyvals(self):
        expected = {'a': 'b', 'c': 'd'}
        self.assertEqual(expected, utils.parse_keyvals("a=b,c=d"))
        self.assertEqual(expected, utils.parse_keyvals("a:b/c:d", '/', ':'))

    def test_extract_domain_or_image_args(self):
        args1 = ['--something', '-d', 'domain', 'somethingelse']
        args2 = ['-b', '--something', '-a', 'image', 'somethingelse']
        args3 = ['-b', '-c', '--something']

        self.assertEqual(['-d', 'domain'],
                         utils.extract_domain_or_image_args(args1))
        self.assertEqual(['-a', 'image'],
                         utils.extract_domain_or_image_args(args2))
        self.assertRaises(ValueError,
                          utils.extract_domain_or_image_args, args3)

    def test_extract_image_args_from_disks(self):
        args1 = ['--disk', '/path/to/image,opt1=val1,opt2=val2']
        args2 = ['--disk', 'opt1=val1,path=/path/to/image,opt2=val2']
        args3 = ['-b', '-c', '--something']

        self.assertEqual(['-a', '/path/to/image'],
                         utils.extract_image_args_from_disks(args1))
        self.assertEqual(['-a', '/path/to/image'],
                         utils.extract_image_args_from_disks(args2))
        self.assertRaises(ValueError,
                          utils.extract_domain_or_image_args, args3)
