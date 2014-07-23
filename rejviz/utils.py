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
