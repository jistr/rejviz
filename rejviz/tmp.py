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

import os
from os import path
import random
import shutil


TMP_DIR_BASE = '/tmp/rejviz-builder-'


def create_dir():
    tmp_dir = _random_dir_name()
    while (path.exists(tmp_dir)):
        tmp_dir = _random_dir_name()
    os.mkdir(tmp_dir, 0o0700)
    return tmp_dir


def remove_dir(tmp_dir):
    if tmp_dir.find(TMP_DIR_BASE) == 0:
        shutil.rmtree(tmp_dir)
    else:
        raise ValueError(
            "Wanted to remove \'%(to_remove)s\' but only directories"
            "beginning with \'%(prefix)s\' can be removed."
            % {'to_remove': tmp_dir, 'prefix': TMP_DIR_BASE})


def _random_dir_name():
    return TMP_DIR_BASE + str(random.randint(1, 999999))
