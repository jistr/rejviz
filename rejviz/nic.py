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


def _nic_values_to_args(nic_values, tmp_dir):
    pass
