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

from dracclient.resources import uris
from dracclient import utils


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

    def list_ilm_settings(self):
        """
        """

        result = {}
        namespaces = [(uris.DCIM_iDRACCardEnumeration, iDRACCardEnumerableAttribute),
                      (uris.DCIM_iDRACCardString, iDRACCardStringAttribute),
                      (uris.DCIM_iDRACCardInteger, iDRACCardIntegerAttribute)]
        for (namespace, attr_cls) in namespaces:
            attribs = self._get_config(namespace, attr_cls)
            if not set(result).isdisjoint(set(attribs)):
                raise exceptions.DRACOperationFailed(
                    drac_messages=('Colliding attributes %r' % (
                        set(result) & set(attribs))))
            result.update(attribs)
        return result

class iDRACCardAttribute(object):
    """Generic iDRACCard attribute class"""

    def __init__(self, name, current_value, pending_value, read_only):
        """Creates iDRACCardAttribute object

        :param name: name of the iDRACCard attribute
        :param current_value: current value of the iDRACCard attribute
        :param pending_value: pending value of the iDRACCard attribute,
        reflecting an unprocessed change (eg. config job not completed)
        :param read_only: indicates whether this iDRACCard attribute 
        can be changed
        """
        self.name = name
        self.current_value = current_value
        self.pending_value = pending_value
        self.read_only = read_only

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def parse(cls, namespace, bios_attr_xml):
        """Parses XML and creates iDRACCardAttribute object"""

        name = utils.get_wsman_resource_attr(
            bios_attr_xml, namespace, 'AttributeName')
        current_value = utils.get_wsman_resource_attr(
            bios_attr_xml, namespace, 'CurrentValue', nullable=True)
        pending_value = utils.get_wsman_resource_attr(
            bios_attr_xml, namespace, 'PendingValue', nullable=True)
        read_only = utils.get_wsman_resource_attr(
            bios_attr_xml, namespace, 'IsReadOnly')

        return cls(name, current_value, pending_value, (read_only == 'true'))


class iDRACCardnumerableAttribute(iDRACCardAttribute):
    """Enumerable iDRACCard attribute class"""

    namespace = uris.DCIM_iDRACCardEnumeration

    def __init__(self, name, current_value, pending_value, read_only,
                 possible_values):
        """Creates iDRACCardEnumerableAttribute object

        :param name: name of the iDRACCard attribute
        :param current_value: current value of the iDRACCard attribute
        :param pending_value: pending value of the iDRACCard attribute,
        reflecting an unprocessed change (eg. config job not completed)
        :param read_only: indicates whether this iDRACCard attribute
        can be changed
        :param possible_values: list containing the allowed values for
        the iDRACCard attribute
        """
        super(iDRACCardEnumerableAttribute, self).__init__(name, current_value,
                                                      pending_value, read_only)
        self.possible_values = possible_values

    @classmethod
    def parse(cls, bios_attr_xml):
        """Parses XML and creates iDRACCardEnumerableAttribute object"""

        bios_attr = iDRACCardAttribute.parse(cls.namespace, bios_attr_xml)
        possible_values = [attr.text for attr
                           in utils.find_xml(bios_attr_xml, 'PossibleValues',
                                             cls.namespace, find_all=True)]

        return cls(bios_attr.name, bios_attr.current_value,
                   bios_attr.pending_value, bios_attr.read_only,
                   possible_values)

    def validate(self, new_value):
        """Validates new value"""

        if str(new_value) not in self.possible_values:
            msg = ("Attribute '%(attr)s' cannot be set to value '%(val)s'."
                   " It must be in %(possible_values)r.") % {
                       'attr': self.name,
                       'val': new_value,
                       'possible_values': self.possible_values}
            return msg


class iDRACCardStringAttribute(iDRACCardAttribute):
    """String iDRACCard attribute class"""

    namespace = uris.DCIM_iDRACCardString

    def __init__(self, name, current_value, pending_value, read_only,
                 min_length, max_length, pcre_regex):
        """Creates iDRACCardStringAttribute object

        :param name: name of the iDRACCard attribute
        :param current_value: current value of the iDRACCard attribute
        :param pending_value: pending value of the iDRACCard attribute,
        reflecting an unprocessed change (eg. config job not completed)
        :param read_only: indicates whether this iDRACCard attribute
        can be changed
        :param min_length: minimum length of the string
        :param max_length: maximum length of the string
        :param pcre_regex: is a PCRE compatible regular expression that 
        the string must match
        """
        super(iDRACCardStringAttribute, self).__init__(name, current_value,
                                                  pending_value, read_only)
        self.min_length = min_length
        self.max_length = max_length
        self.pcre_regex = pcre_regex

    @classmethod
    def parse(cls, bios_attr_xml):
        """Parses XML and creates iDRACCardStringAttribute object"""

        bios_attr = iDRACCardAttribute.parse(cls.namespace, bios_attr_xml)
        min_length = int(utils.get_wsman_resource_attr(
            bios_attr_xml, cls.namespace, 'MinLength'))
        max_length = int(utils.get_wsman_resource_attr(
            bios_attr_xml, cls.namespace, 'MaxLength'))
        pcre_regex = utils.get_wsman_resource_attr(
            bios_attr_xml, cls.namespace, 'ValueExpression', nullable=True)

        return cls(bios_attr.name, bios_attr.current_value,
                   bios_attr.pending_value, bios_attr.read_only,
                   min_length, max_length, pcre_regex)

    def validate(self, new_value):
        """Validates new value"""

        if self.pcre_regex is not None:
            regex = re.compile(self.pcre_regex)
            if regex.search(str(new_value)) is None:
                msg = ("Attribute '%(attr)s' cannot be set to value '%(val)s.'"
                       " It must match regex '%(re)s'.") % {
                           'attr': self.name,
                           'val': new_value,
                           're': self.pcre_regex}
                return msg

class iDRACCardIntegerAttribute(iDRACCardAttribute):
    """Integer iDRACCard attribute class"""

    namespace = uris.DCIM_iDRACCardInteger

    def __init__(self, name, current_value, pending_value, read_only,
                 lower_bound, upper_bound):
        """Creates iDRACCardIntegerAttribute object

        :param name: name of the iDRACCard attribute
        :param current_value: current value of the iDRACCard attribute
        :param pending_value: pending value of the iDRACCard attribute,
        reflecting an unprocessed change (eg. config job not completed)
        :param read_only: indicates whether this iDRACCard attribute
        can be changed
        :param lower_bound: minimum value for the iDRACCard attribute
        :param upper_bound: maximum value for the BOIS attribute
        """
        super(iDRACCardIntegerAttribute, self).__init__(name, current_value,
                                                   pending_value, read_only)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    @classmethod
    def parse(cls, bios_attr_xml):
        """Parses XML and creates iDRACCardIntegerAttribute object"""

        bios_attr = iDRACCardAttribute.parse(cls.namespace, bios_attr_xml)
        lower_bound = utils.get_wsman_resource_attr(
            bios_attr_xml, cls.namespace, 'LowerBound')
        upper_bound = utils.get_wsman_resource_attr(
            bios_attr_xml, cls.namespace, 'UpperBound')

        if bios_attr.current_value:
            bios_attr.current_value = int(bios_attr.current_value)
        if bios_attr.pending_value:
            bios_attr.pending_value = int(bios_attr.pending_value)

        return cls(bios_attr.name, bios_attr.current_value,
                   bios_attr.pending_value, bios_attr.read_only,
                   int(lower_bound), int(upper_bound))

    def validate(self, new_value):
        """Validates new value"""

        val = int(new_value)
        if val < self.lower_bound or val > self.upper_bound:
            msg = ('Attribute %(attr)s cannot be set to value %(val)d.'
                   ' It must be between %(lower)d and %(upper)d.') % {
                       'attr': self.name,
                       'val': new_value,
                       'lower': self.lower_bound,
                       'upper': self.upper_bound}
            return msg

