#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#	  http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections

from dracclient.resources import uris
from dracclient import utils
from dracclient import wsman

DRACRemoteService = collections.namedtuple(
    'DRACRemoteService',
    ['name', 'enabled']
)


REMOTE_SERVICES = {
	"ipmi": "iDRAC.Embedded.1#IPMILan.1#Enable",
	"racadm": "iDRAC.Embedded.1#Racadm.1#Enable",
	"snmp": "iDRAC.Embedded.1#SNMP.1#AgentEnable",
	"ssh": "iDRAC.Embedded.1#SSH.1#Enable",
	"telnet": "iDRAC.Embedded.1#Telnet.1#Enable",
	"vnc": "iDRAC.Embedded.1#VNCServer.1#Enable",
	"web": "iDRAC.Embedded.1#WebServer.1#Enable"
}

REVERSE_REMOTE_SERVICES = dict((v, k) for (k, v) in REMOTE_SERVICES.items())

class LifecycleControllerManagement(object):

    def __init__(self, client):
	"""Creates LifecycleControllerManagement object

	:param client: an instance of WSManClient
	"""
	self.client = client

    def get_version(self):
	"""Returns the Lifecycle controller version

	:returns: Lifecycle controller version as a tuple of integers
	:raises: WSManRequestFailure on request failures
	:raises: WSManInvalidResponse when receiving invalid response
	:raises: DRACOperationFailed on error reported back by the DRAC
		 interface
	"""

	filter_query = ('select LifecycleControllerVersion '
			'from DCIM_SystemView')
	doc = self.client.enumerate(uris.DCIM_SystemView,
				    filter_query=filter_query)
	lc_version_str = utils.find_xml(doc, 'LifecycleControllerVersion',
					uris.DCIM_SystemView).text

	return tuple(map(int, (lc_version_str.split('.'))))

    def get_status(self):
	"""
	"""

	selectors = {
		"Name": "DCIM:LCService",
		"SystemName": "DCIM:ComputerSystem",
		"CreationClassName": "DCIM_LCService",
		"SystemCreationClassName": "DCIM_ComputerSystem"
	}

	doc = self.client.invoke(uris.DCIM_LCService, "GetRSStatus", selectors)

	lc_status = utils.find_xml(doc, 'Status', uris.DCIM_LCService).text

	return(lc_status)

    def set_admin_password(self, password):
	"""
	"""

	selectors = {"Name": "DCIM:iDRACCardService",
			"SystemName": "DCIM:ComputerSystem",
			"CreationClassName": "DCIM_iDRACCardService",
			"SystemCreationClassName": "DCIM_ComputerSystem"}

	properties = {'Target': 'iDRAC.Embedded.1',
		      'AttributeName': 'Users.2#Password',
		      'AttributeValue': password}

	self.client.invoke(uris.DCIM_iDRACCardService, 'SetAttribute',
			   selectors, properties)
	properties = {'Target': 'iDRAC.Embedded.1',
		      'ScheduledStartTime': 'TIME_NOW'}

	self.client.invoke(uris.DCIM_iDRACCardService,
			   'CreateTargetedConfigJob', selectors, properties)

    def list_remote_services(self):
	"""
	"""

	result = []

	namespace = "DCIM_iDRACCardEnumeration"

	q_filter = "select CurrentValue from %s where %s" % \
	(namespace, " or ".join(["InstanceID='%s'" % x for x in REMOTE_SERVICES.values()]))

	doc = self.client.enumerate(
		resource_uri=uris.DCIM_iDRACCardEnumeration,
		filter_query=q_filter
	)

	items = doc.find('.//{%s}Items' % wsman.NS_WSMAN)
	for item in items:
		name = utils.find_xml(item, 'InstanceID', uris.DCIM_iDRACCardEnumeration).text
		value = utils.find_xml(item, 'CurrentValue', uris.DCIM_iDRACCardEnumeration).text

		result.append(DRACRemoteService(name=REVERSE_REMOTE_SERVICES[name], enabled=True if value == "Enabled" else False))

	return result

    def set_remote_services(self, settings):
	"""
	"""

	selectors = {
		"Name": "DCIM:iDRACCardService",
		"SystemName": "DCIM:ComputerSystem",
		"CreationClassName": "DCIM_iDRACCardService",
		"SystemCreationClassName": "DCIM_ComputerSystem"
	}

	job_properties = {
		'Target': 'iDRAC.Embedded.1',
		'ScheduledStartTime': 'TIME_NOW'
	}

	target="iDRAC.Embedded.1"
	attributes = []
	values = []

	for k,v in settings.items():
		attributes.append("#".join(REMOTE_SERVICES[k].split("#")[1:]))
		values.append("Enabled" if v is True else "Disabled")

	properties = {
		"Target": target,
		"AttributeName": attributes,
		"AttributeValue": values
	}

	self.client.invoke(
		uris.DCIM_iDRACCardService,
		'SetAttributes',
		selectors,
		properties
	)

	self.client.invoke(uris.DCIM_iDRACCardService,
			   'CreateTargetedConfigJob', selectors, job_properties)
