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

from copy import deepcopy
import logging
from os import path
import subprocess

import jinja2

from rejviz import libvirt_nets
from rejviz import utils


LOG = logging.getLogger(__file__)
NIC_CONFIG_DIR = '/etc/sysconfig/network-scripts'
NIC_CONFIG_PREFIX = 'ifcfg-'
NIC_CONFIG_FULL_PREFIX = path.join(NIC_CONFIG_DIR, NIC_CONFIG_PREFIX)
FETCH_SCRIPT_TEMPLATE = path.join(
    path.dirname(path.realpath(__file__)),
    'templates', 'fetch_nic.guestfish.j2')


def process_nic_mappings(args):
    if not _has_nic_mapping_args(args):
        return args

    LOG.info('Looking for NIC configurations in the image...')
    nics = _fetch_nics_from_image(args)
    LOG.info('NICs found: %s', ', '.join([n['name'] for n in nics]))
    for nic in nics:
        LOG.debug('NIC %s: %s', nic['name'], str(nic))

    networks = libvirt_nets.get_libvirt_networks()

    mapped_nics = nics
    if _auto_nic_mappings_enabled(args):
        mapped_nics = _map_nics_auto(nics, networks)

    manual_mappings = _parse_manual_nic_mappings(args)
    mapped_nics = _map_nics_manual(mapped_nics, manual_mappings)

    # TODO(jistr): check mappings' sanity

    return _convert_nic_mappings_args(args, mapped_nics)


def _has_nic_mapping_args(args):
    return '--nic-mappings' in args or '--auto-nic-mappings' in args


def _auto_nic_mappings_enabled(args):
    return '--auto-nic-mappings' in args


def _fetch_nics_from_image(args):
    image_args = utils.extract_image_args_from_disks(args)
    nic_names = _get_nic_names_from_image(image_args)
    command = ['guestfish', '-i', '--ro'] + image_args
    with open(FETCH_SCRIPT_TEMPLATE) as template_file:
        template = jinja2.Template(template_file.read())
    script = template.render(
        nic_config_dir=NIC_CONFIG_DIR,
        nic_config_prefix=NIC_CONFIG_PREFIX,
        nic_names=nic_names)
    LOG.debug('Running guestfish to get NIC config details: %s', str(command))
    fetcher = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = fetcher.communicate(script)
    LOG.debug('guestfish returned: %s', output)
    return _filter_ethernet_nics(_parse_nics_output(output))


def _get_nic_names_from_image(image_args):
    command = ['virt-ls'] + image_args + [NIC_CONFIG_DIR]
    LOG.debug('Running virt-ls to list NIC configs: %s', str(command))
    network_scripts = subprocess.check_output(command).splitlines()
    ifcfg_scripts = [s for s in network_scripts
                     if s.startswith(NIC_CONFIG_PREFIX)]
    prefix_len = len(NIC_CONFIG_PREFIX)
    nic_names = [s[prefix_len:] for s in ifcfg_scripts]
    return nic_names


def _parse_nics_output(output):
    lines = output.splitlines()
    nics = []
    current_nic = {}
    for i, line in enumerate(lines):
        # if line is a separator, start a new NIC
        if line == '@-----':
            nics.append(current_nic)
            current_nic = {}
            continue

        # if line is a key, assign a value
        if line.startswith('@'):
            next_line = lines[i + 1] if i + 1 < len(lines) else None

            if next_line and not next_line.startswith('@'):
                current_nic[line[1:]] = next_line
            # if next line is a key again, assign None to the current key
            else:
                current_nic[line[1:]] = None
    return nics


def _filter_ethernet_nics(nics):
    return [nic for nic in nics
            if nic['type'] and nic['type'].lower() == 'ethernet']


def _map_nics_auto(nics, networks):
    mapped_nics = deepcopy(nics)

    for nic in mapped_nics:
        if not nic.get('network'):
            continue

        for network in networks:
            if network['network'] == nic['network']:
                nic['libvirt_network'] = network['name']

    return mapped_nics


def _map_nics_manual(nics, manual_mappings):
    mapped_nics = deepcopy(nics)

    for nic in mapped_nics:
        if manual_mappings.get(nic['name']):
            nic['libvirt_network'] = manual_mappings[nic['name']]

    return mapped_nics


def _parse_manual_nic_mappings(args):
    if '--nic-mappings' not in args:
        return {}

    raw_mappings = args[args.index('--nic-mappings') + 1]
    keyvals = raw_mappings.split(',')
    return dict(keyval.split('=', 1) for keyval in keyvals)


def _convert_nic_mappings_args(args, mapped_nics):
    def get_nic_names(manual_mappings):
        keyvals = manual_mappings.split(',')
        return [keyval.split('=', 1)[0] for keyval in keyvals]

    inserted_nic_names = set()

    # convert manual mappings
    converted_manual = []
    args_iter = iter(args)
    for arg in args_iter:
        if arg == '--nic-mappings':
            mappings_value = next(args_iter)
            nic_names = get_nic_names(mappings_value)
            inserted_nic_names = inserted_nic_names.union(set(nic_names))
            converted_manual.extend(_network_args(nic_names, mapped_nics))
        else:
            converted_manual.append(arg)

    # convert automatic mappings
    converted_auto = []
    for arg in converted_manual:
        if arg == '--auto-nic-mappings':
            all_nic_names = set(nic['name'] for nic in mapped_nics)
            names_to_insert = all_nic_names.difference(inserted_nic_names)
            inserted_nic_names = inserted_nic_names.union(names_to_insert)
            converted_auto.extend(_network_args(names_to_insert, mapped_nics))
        else:
            converted_auto.append(arg)

    return converted_auto


def _network_args(nic_names, mapped_nics):
    args = []

    for nic_name in nic_names:
        nic = _nic_by_name(nic_name, mapped_nics)
        args.append('--network')
        args.append('network=%(libvirt_network)s,mac=%(hwaddr)s,model=virtio'
                    % nic)

    return args


def _nic_by_name(nic_name, nics):
    for nic in nics:
        if nic['name'] == nic_name:
            return nic
    raise ValueError("NIC with name '%s' not found" % nic_name)
