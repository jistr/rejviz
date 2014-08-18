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

from rejviz import nic_mappings

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def main():
    virt_install_args = _process_args(sys.argv[1:])
    _run_virt_install(virt_install_args)


def _process_args(unprocessed_args):
    return nic_mappings.process_nic_mappings(unprocessed_args)


def _run_virt_install(args):
    command_line = ["virt-install"] + args
    LOG.info("Calling virt-install: %s" % " ".join(command_line))
    subprocess.call(command_line)
