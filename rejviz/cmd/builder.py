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
import sys

import rejviz.tmp as tmp


def main():
    try:
        tmp_dir = tmp.create_dir()
        virt_builder_args = _process_args(sys.argv[1:], tmp_dir)
        _run_virt_builder(virt_builder_args)
    finally:
        tmp.delete_dir(tmp_dir)


def _process_args(args, tmp_dir):
    return args


def _run_virt_builder(args):
    command_line = ["virt-builder"] + args
    subprocess.call(command_line)
