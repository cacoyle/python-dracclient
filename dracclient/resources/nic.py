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

NetworkInterface = collections.namedtuple(
    'NetworkInterface',
    ['id', 'mac'])


class NICManagement(object):

    def __init__(self, client):
        """Creates NICManagement object

        :param client: an instance of WSManClient
        """
        self.client = client

    def list_network_interfaces(self):
        """Returns the list of NICs

        :returns: a list of NetworkInterface objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
        """

        doc = self.client.enumerate(uris.DCIM_NICView)

        network_interfaces = utils.find_xml(doc, 'DCIM_NICView',
                                            uris.DCIM_NICView,
                                            find_all=True)

        return [self._parse_network_interfaces(network_interface)
                for network_interface in network_interfaces]

    def _parse_network_interfaces(self, network_interface):
        """Put something here

        """

        return NetworkInterface(
            id=self._get_network_interface_attr(network_interface, 'FQDD'),
            mac=self._get_network_interface_attr(network_interface,
                                                 'PermanentMACAddress'))

    def _get_network_interface_attr(self, network_interface, attr_name):
        """Put something here

        """

        return utils.get_wsman_resource_attr(
            network_interface, uris.DCIM_NICView, attr_name)
