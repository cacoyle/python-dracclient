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

from dracclient.resources.bios import LC_CONTROLLER_VERSION_12G
from dracclient.resources import lifecycle_controller
from dracclient.resources import uris
from dracclient import utils

System = collections.namedtuple(
    'System',
    ['bios_version', 'express_service_tag', 'ilm_version', 'model',
        'generation', 'service_tag', 'status']
)

Primary_Status = {
    "0": "Unknown",
    "1": "OK",
    "2": "Degraded",
    "3": "Error"
}

LED_Selectors = {
    'SystemCreationClassName': 'DCIM_ComputerSystem',
    'SystemName': 'srv:system',
    'CreationClassName': 'DCIM_SystemManagementService',
    'Name': 'DCIM:SystemManagementService'
}


class SystemInfo(object):

    def __init__(self, client):
        """Creates SystemInfo object

        :param client: an instance of WSManClient
        """
        self.client = client

    def get_system_info(self):
        """Returns system information

        :returns: a System object
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
        """

        doc = self.client.enumerate(uris.DCIM_SystemView)

        system_info = utils.find_xml(doc, 'DCIM_SystemView',
                                     uris.DCIM_SystemView, find_all=True)

        return self._parse_system_info(system_info[0])

    def _parse_system_info(self, system_info):

        return System(
            bios_version=self._get_system_info_attr(
                system_info,
                'BIOSVersionString'),
            express_service_tag=self._get_system_info_attr(
                system_info,
                'ExpressServiceCode'),
            ilm_version=self._get_system_info_attr(
                system_info,
                'LifecycleControllerVersion'),
            model=self._get_system_info_attr(
                system_info,
                'Model'),
            generation=self._get_system_info_attr(
                system_info,
                'SystemGeneration'),
            service_tag=self._get_system_info_attr(
                system_info,
                'ServiceTag'),
            status=Primary_Status[self._get_system_info_attr(
                system_info,
                'PrimaryStatus')]
        )

    def _get_system_info_attr(self, system_info, attr_name):
        return utils.get_wsman_resource_attr(
            system_info, uris.DCIM_SystemView, attr_name)

    def enable_system_led(self):
        controller_version = (
            lifecycle_controller.LifecycleControllerManagement(
                self.client).get_version())

        if controller_version > LC_CONTROLLER_VERSION_12G:
            self.client.invoke(uris.DCIM_SystemManagementService,
                               'IdentifyChassis',
                               LED_Selectors, {"IdentifyState": "1"})
        else:
            pass

    def disable_system_led(self):
        controller_version = (
            lifecycle_controller.LifecycleControllerManagement(
                self.client).get_version())

        if controller_version > LC_CONTROLLER_VERSION_12G:
            self.client.invoke(uris.DCIM_SystemManagementService,
                               'IdentifyChassis',
                               LED_Selectors, {"IdentifyState": "0"})
        else:
            pass
