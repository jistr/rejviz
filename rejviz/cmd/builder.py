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

import logging
import subprocess
import sys

from rejviz import nic
from rejviz import tmp


logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def main():
    try:
        tmp_dir = tmp.create_dir()
        LOG.debug('Created tmp directory %s', tmp_dir)
        virt_builder_args = _process_args(sys.argv[1:], tmp_dir)
        _run_virt_builder(virt_builder_args)
    finally:
        tmp.remove_dir(tmp_dir)
        LOG.debug('Removed tmp directory %s', tmp_dir)


def _process_args(args, tmp_dir):
    processed = nic.process_args(args, tmp_dir)
    return processed


def _run_virt_builder(args):
    command_line = ["virt-builder"] + args
    LOG.info("Calling virt-builder: %s" % " ".join(command_line))
    subprocess.call(command_line)
