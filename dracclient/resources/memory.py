#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections

from dracclient import exceptions
from dracclient.resources import uris
from dracclient import utils

Memory = collections.namedtuple(
    'Memory',
    ['id', 'size'])

class MemoryManagement(object):

    def __init__(self, client):
        """Creates Memoryanagement object

        :param client: an instance of WSManClient
        """
        self.client = client

    def list_memory(self):
        """Returns the list of installed memory

        :returns: a list of Memory objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
	"""

        doc = self.client.enumerate(uris.DCIM_MemoryView)

	installed_memory = utils.find_xml(doc, 'DCIM_MemoryView',
                                          uris.DCIM_MemoryView,
                                          find_all=True)

	return [self._parse_memory(memory)
		for memory in installed_memory]

    def _parse_memory(self, memory):
	return Memory(
	    id=self._get_memory_attr(memory, 'FQDD'),
            size=self._get_memory_attr(memory, 'Size'))

    def _get_memory_attr(self, memory, attr_name):
        return utils.get_wsman_resource_attr(
            memory, uris.DCIM_MemoryView, attr_name)
