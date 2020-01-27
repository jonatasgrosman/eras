import tempfile
import xml.etree.ElementTree as etree

import logging


def register_cardinality(cardinality_map_parent, cardinality_descriptor, map_key):
    if "IRI" in cardinality_descriptor[0][0].attrib:
        key_iri = "IRI"
    else:
        key_iri = "abbreviatedIRI"

    cardinality_property = cardinality_descriptor[0][0].attrib[key_iri]
    cardinality_value = cardinality_descriptor[0].attrib['cardinality']

    if cardinality_property not in cardinality_map_parent:
        cardinality_map_parent[cardinality_property] = {}

    cardinality_map_parent[cardinality_property][map_key] = cardinality_value


def read_ontology_as_dict(raw_ontology):
    try:
        root = etree.fromstring(raw_ontology)
        # root = etree.parse(path).getroot()
        names_list = root.tag.split("}")
        type_file = names_list[1]
        base_name = names_list[0].split("{")[1]

        if type_file != "Ontology":
            return False, "It's not a valid Ontology OWL/XML file."

        else:
            dict_to_return = {"Class": {},
                              "ObjectProperty": {},
                              "DataProperty": {},
                              "Enumerator": {},
                              }
            declarations = root.findall('{' + base_name + '}' + 'Declaration')
            subclassof = root.findall('{' + base_name + '}' + 'SubClassOf')
            classassertion = root.findall('{' + base_name + '}' + 'ClassAssertion')
            objectpropertydomain, objectpropertyrange = root.findall('{' + base_name + '}' + 'ObjectPropertyDomain'), \
                                                        root.findall('{' + base_name + '}' + 'ObjectPropertyRange')

            datapropertydomain, datapropertyrange = root.findall('{' + base_name + '}' + 'DataPropertyDomain'), \
                                                    root.findall('{' + base_name + '}' + 'DataPropertyRange')

            datatypedefinition = root.findall('{' + base_name + '}' + 'DatatypeDefinition')

            cardinality_map = {}

            for d in declarations:
                d_children = d.getchildren()
                for c in d_children:
                    key = c.tag.split("}")[1]
                    if key == 'Class' or key == 'NamedIndividual':
                        key = 'Class'
                        if "IRI" in c.attrib:
                            key_iri = "IRI"
                        else:
                            key_iri = "abbreviatedIRI"
                        dict_to_return[key].update({c.attrib[key_iri]: {"parent": "Thing", "children": [],
                                                                        "domain": [], "range": []}})
                    elif key == 'ObjectProperty' or key == 'DataProperty':
                        if "IRI" in c.attrib:
                            key_iri = "IRI"
                        else:
                            key_iri = "abbreviatedIRI"
                        dict_to_return[key].update({c.attrib[key_iri]: {"domain": [], "range": []}})
                    else:
                        pass

            for s in subclassof:
                s_classes = s.findall('{' + base_name + '}' + 'Class')
                if len(s_classes) == 2:
                    if "IRI" in s_classes[0].attrib:
                        key0_iri = "IRI"
                    else:
                        key0_iri = "abbreviatedIRI"
                    if "IRI" in s_classes[1].attrib:
                        key1_iri = "IRI"
                    else:
                        key1_iri = "abbreviatedIRI"

                    parent = s_classes[1].attrib[key1_iri]
                    child = s_classes[0].attrib[key0_iri]

                    dict_to_return['Class'][s_classes[0].attrib[key0_iri]]['parent'] = parent
                    dict_to_return['Class'][s_classes[1].attrib[key1_iri]]['children'].append(child)

                else:

                    if "IRI" in s_classes[0].attrib:
                        key0_iri = "IRI"
                    else:
                        key0_iri = "abbreviatedIRI"

                    parent = s_classes[0].attrib[key0_iri]

                if parent:

                    if parent not in cardinality_map:
                        cardinality_map[parent] = {}

                    data_min_cardinality = s.findall('{' + base_name + '}' + 'DataMinCardinality')
                    data_max_cardinality = s.findall('{' + base_name + '}' + 'DataMaxCardinality')
                    object_min_cardinality = s.findall('{' + base_name + '}' + 'ObjectMinCardinality')
                    object_max_cardinality = s.findall('{' + base_name + '}' + 'ObjectMaxCardinality')

                    if len(data_min_cardinality) > 0:
                        register_cardinality(cardinality_map[parent], data_min_cardinality, 'min')
                    elif len(data_max_cardinality) > 0:
                        register_cardinality(cardinality_map[parent], data_max_cardinality, 'max')
                    elif len(object_min_cardinality) > 0:
                        register_cardinality(cardinality_map[parent], object_min_cardinality, 'min')
                    elif len(object_max_cardinality) > 0:
                        register_cardinality(cardinality_map[parent], object_max_cardinality, 'max')


            for s in classassertion:
                parent = s.findall('{' + base_name + '}' + 'Class')[0]
                child  = s.findall('{' + base_name + '}' + 'NamedIndividual')[0]

                parent = parent.attrib['IRI' if 'IRI' in parent.attrib else 'abbreviatedIRI']
                child = child.attrib['IRI' if 'IRI' in child.attrib else 'abbreviatedIRI']

                dict_to_return['Class'][child]['parent'] = parent
                dict_to_return['Class'][parent]['children'].append(child)

                    
            for o in objectpropertydomain:
                o_children = o.getchildren()

                if "IRI" in o_children[0].attrib:
                    key0_iri = "IRI"
                else:
                    key0_iri = "abbreviatedIRI"

                '''
                if "IRI" in o_children[1].attrib:
                    key1_iri = "IRI"
                else:
                    key1_iri = "abbreviatedIRI"
                '''

                domains = []

                if len(o_children[1].getchildren()) > 1: # ObjectUnionOf
                    for o1_child in o_children[1].getchildren():
                        if len(o1_child.attrib) != 0:
                            if 'IRI' in o1_child.attrib:
                                domains.append(o1_child.attrib['IRI'])
                            else:
                                domains.append(o1_child.attrib['abbreviatedIRI'])
                elif len(o_children[1].attrib) != 0:
                    if "IRI" in o_children[1].attrib:
                        domains.append(o_children[1].attrib['IRI'])
                    else:
                        domains.append(o_children[1].attrib['abbreviatedIRI'])

                for domain in domains:
                    dict_to_return['Class'][domain]['domain'].append(o_children[0].attrib[key0_iri])
                    dict_to_return['ObjectProperty'][o_children[0].attrib[key0_iri]]['domain'].append(domain)

                '''
                elif len(o_children[1].attrib) != 0:
                    dict_to_return['Class'][o_children[1].attrib[key1_iri]]['domain'].append(o_children[0].attrib[key0_iri])
                    dict_to_return['ObjectProperty'][o_children[0].attrib[key0_iri]]['domain'].append(
                    o_children[1].attrib[key1_iri])
                '''

            for o in objectpropertyrange:
                o_children = o.getchildren()
                if "IRI" in o_children[0].attrib:
                    key0_iri = "IRI"
                else:
                    key0_iri = "abbreviatedIRI"
                if "IRI" in o_children[1].attrib:
                    key1_iri = "IRI"
                else:
                    key1_iri = "abbreviatedIRI"

                if len(o_children[1].attrib) != 0:
                    dict_to_return['Class'][o_children[1].attrib[key1_iri]]['range'].append(o_children[0].attrib[key0_iri])
                    dict_to_return['ObjectProperty'][o_children[0].attrib[key0_iri]]['range'].append(
                        o_children[1].attrib[key1_iri])

            for d in datapropertydomain:
                d_children = d.getchildren()
                if "IRI" in d_children[0].attrib:
                    key0_iri = "IRI"
                else:
                    key0_iri = "abbreviatedIRI"
                if "IRI" in d_children[1].attrib:
                    key1_iri = "IRI"
                else:
                    key1_iri = "abbreviatedIRI"

                if len(d_children[1].attrib) != 0:
                    dict_to_return['Class'][d_children[1].attrib[key1_iri]]['domain'].append(d_children[0].attrib[key0_iri])
                    dict_to_return['DataProperty'][d_children[0].attrib[key0_iri]]['domain'].append(
                        d_children[1].attrib[key1_iri])

            for d in datapropertyrange:
                d_children = d.getchildren()
                if "IRI" in d_children[0].attrib:
                    key0_iri = "IRI"
                else:
                    key0_iri = "abbreviatedIRI"
                if "IRI" in d_children[1].attrib:
                    key1_iri = "IRI"
                else:
                    key1_iri = "abbreviatedIRI"

                if len(d_children[1].attrib) != 0:
                    dict_to_return['Class'].update({d_children[1].attrib[key1_iri]: {"parent": "DataType",
                                                                                     "domain": [], "range": []}})
                    dict_to_return['Class'][d_children[1].attrib[key1_iri]]['range'].append(d_children[0].attrib[key0_iri])
                    dict_to_return['DataProperty'][d_children[0].attrib[key0_iri]]['range'].append(
                        d_children[1].attrib[key1_iri])

            for d in datatypedefinition:
                d_children = d.getchildren()
                if "IRI" in d_children[0].attrib:
                    key0_iri = "IRI"
                else:
                    key0_iri = "abbreviatedIRI"

                if d_children[1].tag.split("}").pop() == 'DataOneOf':
                    tags = d_children[1].getchildren()
                    dict_to_return['Enumerator'].update({d_children[0].attrib[key0_iri]: []})
                    for t in tags:
                        dict_to_return['Enumerator'][d_children[0].attrib[key0_iri]].append(t.text)

            for entity_key in dict_to_return:

                for entity in dict_to_return[entity_key]:

                    if 'domain' in dict_to_return[entity_key][entity]:

                        new_domain = []

                        for entity_property in dict_to_return[entity_key][entity]['domain']:

                            range_description = {'property': entity_property}

                            if entity in cardinality_map and entity_property in cardinality_map[entity]:

                                if 'min' in cardinality_map[entity][entity_property]:
                                    range_description['min'] = cardinality_map[entity][entity_property]['min']
                                if 'max' in cardinality_map[entity][entity_property]:
                                    range_description['max'] = cardinality_map[entity][entity_property]['max']

                            new_domain.append(range_description)

                        dict_to_return[entity_key][entity]['domain'] = new_domain

            return True, dict_to_return

    except Exception as e:
        logging.error(
            """
                Exception: {exception}
            """.format(
                exception=e
            ), exc_info=True
        )
        return False, str(e)


'''
def get_ontology_as_dict(stream, is_bytes_stream=False):
    temp = tempfile.NamedTemporaryFile(mode='wb' if is_bytes_stream else 'w+t')
    temp.seek(0)
    try:
        temp.write(stream.read())
        could_read, dict_to_return = read_ontology_as_dict(temp.name)
        return could_read, dict_to_return
    except Exception as e:
        return False, str(e)
    finally:
        stream.close()
        temp.close()

'''