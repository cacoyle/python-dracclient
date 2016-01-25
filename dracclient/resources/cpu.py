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

from dracclient.resources import uris
from dracclient import utils

CPU = collections.namedtuple(
    'CPU',
    ['id', 'cores'])


class CPUManagement(object):

    def __init__(self, client):
        """Creates CPUManagement object

        :param client: an instance of WSManClient
        """
        self.client = client

    def list_cpus(self):
        """Returns the list of CPUs

        :returns: a list of CPU objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
        """

        doc = self.client.enumerate(uris.DCIM_CPUView)

        cpus = utils.find_xml(doc, 'DCIM_CPUView',
                              uris.DCIM_CPUView,
                              find_all=True)

        return [self._parse_cpus(cpu) for cpu in cpus]

    def _parse_cpus(self, cpu):
        return CPU(id=self._get_cpu_attr(cpu, 'FQDD'),
                   cores=self._get_cpu_attr(cpu, 'NumberOfProcessorCores'))

    def _get_cpu_attr(self, cpu, attr_name):
        return utils.get_wsman_resource_attr(
            cpu, uris.DCIM_CPUView, attr_name)
