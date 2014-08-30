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
import os
from os import path
import random

import jinja2

from rejviz import utils


LOG = logging.getLogger(__file__)
NIC_CONFIG_PREFIX = 'etc/sysconfig/network-scripts/ifcfg-'


def process_args(args, tmp_dir):
    final_args = []
    args_iter = iter(args)
    for arg in args_iter:
        # if not '--nic' or '--nic=something', just pass it untouched
        if arg.find('--nic=') != 0 and arg != '--nic':
            final_args.append(arg)
        # if just '--nic', we're looking for the next element in args
        # array to fetch the values from
        elif arg == '--nic':
            nic_values = next(args_iter)
            final_args += _nic_values_to_args(nic_values, tmp_dir)
        # if specified as '--nic=values', remove the '--nic=' part
        else:
            nic_values = arg[len('--nic='):]
            final_args += _nic_values_to_args(nic_values, tmp_dir)
    return final_args


def _nic_values_to_args(nic_string, tmp_dir):
    LOG.debug("NIC string %s", nic_string)
    nic_vars = _ensure_nic_vars(utils.parse_keyvals(nic_string))
    config_contents = _render_nic_template(nic_vars)
    config_file_path = NIC_CONFIG_PREFIX + nic_vars['name']
    tmp_config_file_path = path.join(tmp_dir, config_file_path)
    tmp_config_dir_path = path.dirname(tmp_config_file_path)
    target_config_file_path = path.join('/', config_file_path)

    if not path.exists(tmp_config_dir_path):
        os.makedirs(tmp_config_dir_path, 0o700)
    with open(tmp_config_file_path, 'w') as config_file:
        config_file.write(config_contents)
    LOG.info("Adding NIC with params %s", str(nic_vars))
    return [
        '--upload',
        ':'.join([tmp_config_file_path, target_config_file_path]),
    ]


def _render_nic_template(nic_vars):
    template_file_name = path.join(
        path.dirname(path.realpath(__file__)), 'templates', 'ifcfg-eth.j2')
    with open(template_file_name) as template_file:
        template = jinja2.Template(template_file.read())

    return template.render(**nic_vars)


def _ensure_nic_vars(nic_vars):
    LOG.debug("NIC vars before processing %s", str(nic_vars))
    new_vars = dict(nic_vars)

    if not new_vars.get('name'):
        raise ValueError("Invalid NIC parameters - name not set: %s"
                         % str(nic_vars))

    new_vars.setdefault('hwaddr', _generate_mac_address())

    if new_vars.get('ipaddr'):
        new_vars.setdefault('bootproto', 'static')

    if new_vars.get('bootproto') == 'static':
        if not new_vars.get('ipaddr'):
            raise ValueError("NIC '%(name)s' - when bootproto is 'static'"
                             "it is required to specify also 'ipaddr'")

        # "123.456.789.123" => "123.456.789."
        ip_prefix = new_vars['ipaddr'][:(new_vars['ipaddr'].rindex('.') + 1)]

        if not new_vars.get('network'):
            new_vars['network'] = ip_prefix + '0'
        if not new_vars.get('netmask'):
            new_vars['netmask'] = '255.255.255.0'
        if not new_vars.get('broadcast'):
            new_vars['broadcast'] = ip_prefix + '255'
    else:
        new_vars['bootproto'] = 'dhcp'
        new_vars.pop('ipaddr', None)
        new_vars.pop('network', None)
        new_vars.pop('netmask', None)
        new_vars.pop('broadcast', None)
        new_vars.pop('gateway', None)
        new_vars.pop('dns1', None)
        new_vars.pop('dns2', None)

    LOG.debug("NIC vars after processing %s", str(new_vars))
    return new_vars


def _generate_mac_address():
    prefix = '52:54:00:'  # 52:54:00 is libvirt default

    def one_group():
        return ''.join([random.choice('0123456789abcdef') for _ in range(2)])

    return prefix + ':'.join([one_group() for _ in range(3)])
