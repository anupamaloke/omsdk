import io
import re
from omsdk.sdkprint import PrettyPrint
from omsdk.typemgr.FieldType import FieldType
from omsdk.typemgr.ClassType import ClassType
from omsdk.typemgr.BuiltinTypes import RootClassType
from omsdk.typemgr.ArrayType import ArrayType
from omsdk.sdkcenum import TypeHelper
import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

class FormatterTemplate(object):
    def __init__(self, everything):
        if PY2:
            super(FormatterTemplate, self).__init__()
        else:
            super().__init__()
        self.everything = everything
        self.include_composite = True
        self.target = None

    def _emit(self, output, value):
        return 0

    def _init(self, output, obj, space, array=False):
        return None

    def _close(self, output, obj, space):
        pass

    def _write_start(self, output, attr_name, value, space):
        pass

    def _write_end(self, output, attr_name, value, data, space):
        pass

    def _get_str(self):
        return None

    def format_type(self, obj):
        if obj:
            self._format_recurse(self.target, obj, space='')
        return self

    def _format_recurse(self, output_obj, obj, space):
        T='  '
        if isinstance(obj, FieldType):
            return self._emit(output_obj, obj)
        opobj = self._init(output_obj, obj, space, isinstance(obj, ArrayType))
        props = obj.Properties
        oldspace = space
        if not isinstance(obj, ArrayType):
            space = space + T
        for i in props:
            if isinstance(i, str):
                if not self.everything:
                    if not obj.__dict__[i].is_changed():
                        continue
                if obj.__dict__[i]._composite and \
                   not self.include_composite:
                    continue
                attr_name = i
                if obj.__dict__[i]._alias is not None:
                    attr_name = obj.__dict__[i]._alias
                attr_name = re.sub('_.*', '', attr_name)
                if obj._fname is None:
                    attr_name = obj._alias + "." + str(obj.__dict__[i]._index) + "#" + attr_name
                if not isinstance(obj.__dict__[i], ClassType) and \
                   not isinstance(obj.__dict__[i], ArrayType):
                    self._write_start(opobj, attr_name, obj.__dict__[i], space)
                retval = self._format_recurse(opobj, obj.__dict__[i], space)
                if not isinstance(obj.__dict__[i], ClassType) and \
                   not isinstance(obj.__dict__[i], ArrayType):
                    self._write_end(opobj, attr_name, obj.__dict__[i], space, retval)
            else:
                if not self.everything and not i.is_changed():
                    continue
                entry = self._create_array_entry(opobj)
                entry = self._format_recurse(entry, i, space)
                entry = self._close_array_entry(opobj, entry)
        space = oldspace
        self._close(opobj, obj, space, isinstance(obj, ArrayType))
        return opobj

    def printx(self):
        print(self._get_str())

class XMLFormatter(FormatterTemplate):
    def __init__(self, everything):
        super().__init__(everything)
        self.target = io.StringIO()
        self.include_composite = False

    def _emit(self, output, value):
        val = value.sanitized_value()
        if val: output.write(str(val))
        return 0

    def _init(self, output, obj, space, array=False):
        if obj._fname and not array:
            output.write(space + '<{0}'.format(obj._fname))
            for i in obj._attribs:
                output.write(' {0}="{1}"'.format(i, obj._attribs[i])) 
            output.write('>\n') 
        return output

    def _close(self, output, obj, space, array=False):
        if obj._fname and not array:
            output.write(space +'</{0}>\n'.format(obj._fname))

    def _create_array_entry(self, output):
        return output

    def _close_array_entry(self, opobj, obj):
        return 

    def _write_start(self, output, attr_name, value, space):
        if value._fname:
            output.write(space+'<{0} name="{1}">'.  format(value._fname, attr_name))
            if not isinstance(value, FieldType):
                output.write('\n')

    def _write_end(self, output, attr_name, value, data, space):
        if value._fname:
            output.write('</{0}>\n'.format(value._fname))

    def _get_str(self):
        return self.target.getvalue()

