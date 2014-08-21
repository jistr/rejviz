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

from six.moves import reduce


def parse_keyvals(keyvals_string, item_separator=',', kv_separator='='):
    keyvals_raw = keyvals_string.split(item_separator)

    def keyvals_to_hash(keyvals, item):
        key, value = item.split(kv_separator, 1)
        keyvals[key] = value
        return keyvals

    return reduce(keyvals_to_hash, keyvals_raw, {})


def extract_domain_or_image_args(args):
    if '-d' in args:
        return ['-d', args[args.index('-d') + 1]]
    elif '-a' in args:
        return ['-a', args[args.index('-a') + 1]]
    else:
        raise ValueError("No -d or -a found in arguments.")


def extract_image_args_from_disks(args):
    def image_from_disk_opts(raw_opts):
        opts = raw_opts.split(',')

        # --disk /some/storage/path[,opt1=val1]...
        if opts[0].find('=') == -1:
            return opts[0]

        # --disk opt1=val1,opt2=val2,...  (looking for 'path' option)
        for optval in opts:
            opt, val = optval.split('=', 1)
            if opt == 'path':
                return val

        raise ValueError("Disk options '%s' do not contain an image path."
                         % raw_opts)

    if '--disk' in args:
        return ['-a', image_from_disk_opts(args[args.index('--disk') + 1])]
    else:
        raise ValueError("No --disk found in arguments.")
