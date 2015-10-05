import json
import xml.etree.ElementTree as ET

from collections import OrderedDict


def get_constant(element):
    constant_name = element.attrib['name']
    constant_value = element.attrib['value']
    return "%s = %s%s" % (constant_name.upper().replace("-", "_"), constant_value, "\n")


def write_classes(root, out):
    method_classes = root.findall("class")
    class_methods_dict = OrderedDict()
    for method_class in method_classes:
        class_id, class_name, class_methods = get_class_data(method_class)
        class_methods_dict[class_id] = {'name': class_name, 'methods': class_methods}
    # json.dumps converts int keys to strings so have to do it manually
    out.write("AMQP_METHODS = {\n")
    for class_index in class_methods_dict:
        out.write("%d: \n{\n" % class_index)
        methods_dict = class_methods_dict[class_index]['methods']
        for method_index in methods_dict:
            out.write("%d: \"%s.%s\",\n" % (method_index, class_methods_dict[class_index]['name'], methods_dict[method_index]['name']))
        out.write("},\n")
    out.write("}\n")


def get_class_data(method_class):
    method_dict = OrderedDict()
    methods = method_class.findall("method")
    for method in methods:
        method_dict[int(method.attrib['index'])] = {'name': method.attrib['name']}
    return int(method_class.attrib['index']), method_class.attrib['name'], method_dict


def extract_data(root, out):
    constants = root.findall("constant")
    constant_declarations = []
    for constant in constants:
        constant_declarations.append(get_constant(constant))
    constant_declarations.sort()
    for constant_declaration in constant_declarations:
        out.write(constant_declaration)
    out.write("\n")

    write_classes(root, out)


def main():
    tree = ET.parse('amqp0-9-1.xml')
    root = tree.getroot()
    with open('amqp_constants.py', 'w') as f:
        extract_data(root, f)
        
if __name__ == '__main__':
    main()