import re
from omsdk.typemgr.FieldType import FieldType
from omsdk.typemgr.ClassType import ClassType
from omsdk.sdkcenum import EnumWrapper
import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

AddressTypes = EnumWrapper("ADT", {
    'IPv4Address' : 1,
    'IPv6Address' : 2,
    'IPAddress' : 3,
    'MACAddress' :  4,
    'WWPNAddress' : 5,
}).enum_type

class CompositeFieldType(FieldType):
    def __init__(self, *parts):
        if PY2:
            super(CompositeFieldType, self).__init__(None, tuple, 'Attribute', None, None, True)
        else:
            super().__init__(None, tuple, 'Attribute', None, None, True)
        self.__dict__['_value'] = parts
        self._composite = True

    def clone(self, parent=None):
        return type(self)(*self.__dict__['_value'])

    def get_value(self):
        return [i for i in self._value if i and i not in ['']]

    def set_value(self, value):
        raise AttributeError('cannot modify composite field')

class RootClassType(ClassType):
    def __init__(self, fname, alias, parent = None):
        if PY2:
            super(RootClassType, self).__init__(fname, alias, parent)
        else:
            super().__init__(fname, alias, parent)

class CloneableFieldType(FieldType):
    def clone(self, parent=None, commit=False):
        if isinstance(self, EnumTypeField):
            return type(self)(self._value, entype=self._type, alias=self._alias,
                  parent=parent, volatile=self._volatile,
                  modifyAllowed = self._modifyAllowed,
                  deleteAllowed = self._deleteAllowed,
                  rebootRequired = self._rebootRequired,
                  loading_from_scp=not commit)
        else:
            return type(self)(self._value, alias=self._alias,
                  parent=parent, volatile=self._volatile,
                  modifyAllowed = self._modifyAllowed,
                  deleteAllowed = self._deleteAllowed,
                  rebootRequired = self._rebootRequired,
                  loading_from_scp=not commit)

class PortField(CloneableFieldType):
    def __init__(self, init_value, alias =None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(PortField, self).__init__(init_value, int, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, int, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)

    def my_accept_value(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(str(value) + " should be an integer > 0")
        return True
        
class IntField(CloneableFieldType):
    def __init__(self, init_value, alias =None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(IntField, self).__init__(init_value, int, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, int, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)

class BooleanField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(BooleanField, self).__init__(init_value, bool, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, bool, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)

class StringField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(StringField, self).__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)

class EnumTypeField(CloneableFieldType):
    def __init__(self, init_value, entype, alias=None, parent=None,
                 volatile=False, modifyAllowed=True, deleteAllowed=True,
                 rebootRequired=False):
        if PY2:
            super(EnumTypeField, self).__init__(init_value, entype, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, entype, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)


class AddressHelpers(object):
    @staticmethod
    def _check_address(value, address_type):
        match_regex = []
        if address_type in [AddressTypes.IPv4Address, AddressTypes.IPAddress]:
            match_regex.append('^\d+([.]\d+){3}$')
        elif address_type in [AddressTypes.IPv6Address, AddressTypes.IPAddress]:
            match_regex.append('^[a-f0-9:]+$')
        elif address_type in [AddressTypes.MACAddress]:
            match_regex.append('^[0-9a-f]{2}(:[0-9a-f]{2}){5}$')
        elif address_type in [AddressTypes.WWPNAddress]:
            match_regex.append('^[0-9a-f]{2}(:[0-9a-f]{2}){7}$')

        if value is None or value == '':
            return True

        if not isinstance(value, str):
            return False

        for pattern in match_regex:
            if not re.match(pattern, value):
                return False

        if address_type in [AddressTypes.IPv4Address, AddressTypes.IPAddress] \
           and ':' not in value:
            for n in value.split('.'):
                if int(n) > 255:
                    return False
        return True

class IPv4AddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(IPv4AddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)

    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.IPv4Address)

class IPv6AddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(IPv6AddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.IPv6Address)

class IPAddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(IPAddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)

    # Accepts both IPv4 and IPv6
    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.IPAddress)

class MacAddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(MacAddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)

    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.MACAddress)

class WWPNAddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                modifyAllowed=True, deleteAllowed=True, rebootRequired=False):
        if PY2:
            super(WWPNAddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                         volatile, modifyAllowed, deleteAllowed, rebootRequired)

    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.WWPNAddress)
