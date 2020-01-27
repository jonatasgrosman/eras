from copy import copy

import gridfs
import module.util.ontologyReader as OntologyReader
from bson.objectid import ObjectId
from module import db
from module.service.serviceException import ServiceException
from module.util.mongoUtil import mongo_result_wrapper
import module.util.objectUtil as ObjectUtil


def project_result_handler(projects, append_documents_packages, append_documents_package_statistics):

    import module.service.documentPackageService as DocumentPackageService

    for project in projects:

        if 'annotationGuidelines' in project and 'id' not in project['annotationGuidelines']:
            del project['annotationGuidelines']

        if append_documents_packages or append_documents_package_statistics:

            project['documentPackages'] = DocumentPackageService.get_document_packages_by_project(str(project['id']), False)

        if append_documents_package_statistics:

            for document_package in project['documentPackages']:
                document_package['statistics'] = DocumentPackageService.get_document_package_status_statistics(
                    document_package['id'])

    return projects


def check_project(project_id):

    if not project_id:
        raise ServiceException('INVALID PROJECT ID')

    project = get_project(project_id)

    if not project:
        raise ServiceException('INVALID PROJECT ID')

    return project


@mongo_result_wrapper()
def get_projects(owner=None, project_ids=[], skip=None, limit=None, append_documents_packages=True,
                 append_documents_package_statistics=False):

    match = {}
    if owner:
        match['owner'] = owner

    if project_ids and len(project_ids) > 0:
        project_ids = [ObjectId(v) for v in project_ids]
        match['_id'] = {'$in': project_ids}

    query_flow = [
        {'$match': match},
        {'$project': {
            '_id': 0,
            'id': '$_id',
            'owner': 1,
            'name': 1,
            'language': 1,
            'entities': 1,
            'smartSentenceSegmentation': 1,
            'smartWordSegmentation': 1,
            'textReplacements': 1,
            'ontology': {'id': '$ontology._id', 'name': '$ontology.name'},
            'annotationGuidelines': {'id': '$annotationGuidelines._id', 'name': '$annotationGuidelines.name'}
        }}
    ]

    if skip:
        query_flow.append({'$skip': int(skip)})

    if limit:
        query_flow.append({'$limit': int(limit)})

    cursor = db.projects.aggregate(query_flow)

    return project_result_handler(list(cursor), append_documents_packages, append_documents_package_statistics)


@mongo_result_wrapper(is_single_result=True)
def get_project(project_id, append_documents_packages=True, append_documents_package_statistics=False):

    return get_projects(project_ids=[project_id], append_documents_packages=append_documents_packages,
                        append_documents_package_statistics=append_documents_package_statistics)


@mongo_result_wrapper(is_insert=True)
def create_project(owner, name, language, smartSentenceSegmentation, smartWordSegmentation, text_replacements,
                   ontology, annotation_guidelines):

    if not ontology:
        raise ServiceException('ONTOLOGY CANNOT BE NULL')

    to_insert = {
        'name': name,
        'owner': owner,
        'language': language,
        'smartSentenceSegmentation': smartSentenceSegmentation,
        'smartWordSegmentation': smartWordSegmentation,
        'textReplacements': text_replacements
    }

    ontology_file_id = gridfs.GridFS(db).put(ontology['bytes'], filename=ontology['name'], contentType=ontology['type'])

    to_insert['ontology'] = {'_id': ontology_file_id, 'name': ontology['name']}

    if annotation_guidelines:
        annotation_guidelines_file_id = gridfs.GridFS(db).put(annotation_guidelines['bytes'],
                                                              filename=annotation_guidelines['name'],
                                                              contentType=annotation_guidelines['type'])
        to_insert['annotationGuidelines'] = {'_id': annotation_guidelines_file_id,
                                             'name': annotation_guidelines['name']}

    insetion = db.projects.insert_one(to_insert)

    build_entities(insetion.inserted_id)

    return insetion


def update_project(project_id, name, smartSentenceSegmentation, smartWordSegmentation, text_replacements):

    check_project(project_id)

    db.projects.update({
        '_id': ObjectId(project_id)
    }, {
        '$set': {
            'name': name,
            'smartSentenceSegmentation': smartSentenceSegmentation,
            'smartWordSegmentation': smartWordSegmentation,
            'textReplacements': text_replacements
        }
    })


def remove_project(project_id):

    project = check_project(project_id)

    gridfs.GridFS(db).delete(ObjectId(project['ontology']['id']))
    if 'annotationGuidelines' in project:
        gridfs.GridFS(db).delete(ObjectId(project['annotationGuidelines']['id']))

    import module.service.documentPackageService as DocumentPackageService
    DocumentPackageService.remove_document_package_by_project(project_id)

    db.projects.delete_one({
        '_id': ObjectId(project_id)
    })


def update_project_ontology(project_id, ontology):

    if not ontology:
        raise ServiceException('ONTOLOGY CANNOT BE NULL')

    project = check_project(project_id)

    gridfs.GridFS(db).delete(ObjectId(project['ontology']['id']))
    ontology_file_id = gridfs.GridFS(db).put(ontology['bytes'], filename=ontology['name'], contentType=ontology['type'])
    ontology_object = {'_id': ontology_file_id, 'name': ontology['name']}

    db.projects.update({
        '_id': ObjectId(project_id)
    }, {
        '$set': {
            'ontology': ontology_object
        }
    })

    build_entities(project_id)

    return str(ontology_file_id)

def update_project_entities(project_id, entities):

    check_project(project_id)

    db.projects.update({
        '_id': ObjectId(project_id)
    }, {
        '$set': {
            'entities': entities
        }
    })

def build_entities(project_id):

    ontology_map = get_ontology_tree(project_id)

    def fill_entities_list(entities_dict, entities_list):
        entity_labels = list(entities_dict.keys())
        entity_labels.sort()

        for entity_label in entity_labels:
            relations = []
            children = []

            if 'children' in entities_dict[entity_label]:
                fill_entities_list(entities_dict[entity_label]['children'], children)
            if 'relations' in entities_dict[entity_label]:

                relation_labels = list(entities_dict[entity_label]['relations'].keys())
                relation_labels.sort()
                
                for relation_label in relation_labels:
                    relations.append({'label': relation_label, 'enabled': True, 'targets': entities_dict[entity_label]['relations'][relation_label]})

            entity = {'label': entity_label, 'enabled': True, 'relations': relations, 'children': children}
            entities_list.append(entity)
    
    entities = []
    fill_entities_list(ontology_map, entities)

    db.projects.update({
        '_id': ObjectId(project_id)
    }, {
        '$set': {
            'entities': entities
        }
    })


def update_annotation_guidelines(project_id, annotation_guidelines):

    project = check_project(project_id)

    if 'annotationGuidelines' in project:
        gridfs.GridFS(db).delete(ObjectId(project['annotationGuidelines']['id']))

    annotation_guidelines_file_id = gridfs.GridFS(db).put(annotation_guidelines['bytes'],
                                                          filename=annotation_guidelines['name'],
                                                          contentType=annotation_guidelines['type'])
    annotation_guidelines_object = {'_id': annotation_guidelines_file_id, 'name': annotation_guidelines['name']}

    db.projects.update({
        '_id': ObjectId(project_id)
    }, {
        '$set': {
            'annotationGuidelines': annotation_guidelines_object
        }
    })

    return str(annotation_guidelines_file_id)


def remove_annotation_guidelines(project_id):

    project = check_project(project_id)

    if 'annotationGuidelines' in project:
        gridfs.GridFS(db).delete(ObjectId(project['annotationGuidelines']['id']))

    db.projects.update({
        '_id': ObjectId(project_id)
    }, {
        '$unset': {
            'annotationGuidelines': ''
        }
    })


def get_ontology(project_id):

    project = check_project(project_id)

    if 'ontology' in project:
        return gridfs.GridFS(db).get(ObjectId(project['ontology']['id']))


def get_ontology_summary(project_id):

    ontology = get_ontology(project_id)

    ontology_string = ontology.read().decode('UTF-8')

    could_read, result = OntologyReader.read_ontology_as_dict(ontology_string)

    if could_read:
        return result


def get_ontology_tree(project_id):

    ontology_summary = get_ontology_summary(project_id)

    properties_by_domain = {}

    def fill_properties_by_domain(map_key):

        data_properties = list(ontology_summary[map_key].keys())
        for data_property in data_properties:
            for property_domain in ontology_summary[map_key][data_property]['domain']:
                property_domain_name = property_domain['property']
                if property_domain_name not in properties_by_domain:
                    properties_by_domain[property_domain_name] = {}
                if data_property not in properties_by_domain[property_domain_name]:
                    properties_by_domain[property_domain_name][data_property] = []
                for property_range in ontology_summary[map_key][data_property]['range']:
                    properties_by_domain[property_domain_name][data_property].append(property_range)

    fill_properties_by_domain('DataProperty')
    fill_properties_by_domain('ObjectProperty')

    ontology_summary_class_keys = list(ontology_summary['Class'].keys())
    node_by_name = {'Thing': {'children': {}}, 'DataType': {'children': {}}}

    def append_node(parent_node_name, node_key, node_name):
        new_node = {'children': {}, 'relations': {}, 'inheritedRelations': {}, 'ancestors': [parent_node_name]}
        parent_node = node_by_name[parent_node_name]

        if 'ancestors' in parent_node:
            new_node['ancestors'] = parent_node['ancestors'] + new_node['ancestors']

        parent_node['children'][node_name] = new_node
        node_by_name[node_name] = new_node

        if node_key in properties_by_domain:
            for property in list(properties_by_domain[node_key]):
                new_node['relations'][property] = properties_by_domain[node_key][property]

        if 'relations' in parent_node:
            new_node['inheritedRelations'] = ObjectUtil.merge_dicts(parent_node['relations'], new_node['inheritedRelations'])
        if 'inheritedRelations' in parent_node:
            new_node['inheritedRelations'] = ObjectUtil.merge_dicts(parent_node['inheritedRelations'], new_node['inheritedRelations'])

    keep_searching = True
    while keep_searching:

        keep_searching = False

        for class_name in list(ontology_summary_class_keys):

            parent = ontology_summary['Class'][class_name]['parent']

            if parent in node_by_name:

                keep_searching = True

                if 'Enumerator' in ontology_summary and class_name in ontology_summary['Enumerator']:
                    for enumerator_value in ontology_summary['Enumerator'][class_name]:
                        enumerator_key = class_name + ':' + enumerator_value
                        append_node(parent, class_name, enumerator_key)
                else:
                    append_node(parent, class_name, class_name)

                ontology_summary_class_keys.remove(class_name)

    ontology_tree = ObjectUtil.merge_dicts(node_by_name['Thing']['children'], node_by_name['DataType']['children'])

    return ontology_tree


def get_ontology_map(project_id):

    ontology_summary = get_ontology_summary(project_id)

    ontology_map = {}

    max_cardinality_map = {}

    def get_level(entity):
        if entity['parent'] == 'Thing' or entity['parent'] == 'DataType':
            return 0
        else:
            parent = ontology_summary['Class'][entity['parent']]
            return 1 + get_level(parent)

    entities_name = list(ontology_summary['Class'].keys())
    entities_name.sort(key=lambda x: get_level(ontology_summary['Class'][x]))
    entities_name.reverse()

    # CREATING DESCENDANTS MAP

    descendants_by_entity = {}
    
    for entity_name in entities_name:

        entity = ontology_summary['Class'][entity_name]

        max_cardinality_map[entity_name] = {}
        
        for relation in entity['domain']:
            if 'max' in relation:
                max_cardinality_map[entity_name][relation['property']] = relation['max']

        if 'parent' in entity and entity['parent'] != 'Thing' and entity['parent'] != 'DataType':
            if entity['parent'] not in descendants_by_entity:
                descendants_by_entity[entity['parent']] = {}

            descendants_by_entity[entity['parent']][entity_name] = True

            if entity_name in descendants_by_entity:

                for descendant in descendants_by_entity[entity_name].keys():
                    descendants_by_entity[entity['parent']][descendant] = True

    relations_by_domain = {}
    enumerators_by_entity = {}

    # CREATING DATAPROPERTY MAP
    
    for property_key in ontology_summary['DataProperty'].keys():
        data_property = ontology_summary['DataProperty'][property_key]
        
        for domain in data_property['domain']:
            
            if domain['property'] not in relations_by_domain:
                relations_by_domain[domain['property']] = []
            
            relations = relations_by_domain[domain['property']]
            
            for data_range in data_property['range']:
                relations.append({'range': data_range, 'property': property_key})
                
    # CREATING OBJECTPROPERTY MAP
    
    for property_key in ontology_summary['ObjectProperty'].keys():
        object_property = ontology_summary['ObjectProperty'][property_key]
    
        for domain in object_property['domain']:
            if domain['property'] not in relations_by_domain:
                relations_by_domain[domain['property']] = []
            
            relations = relations_by_domain[domain['property']]

            for data_range in object_property['range']:
                relations.append({'range': data_range, 'property': property_key})
                
    # CREATING ENUMERATORS MAP
    for entity_key in ontology_summary['Enumerator'].keys():
        enumerators_by_entity[entity_key] = ontology_summary['Enumerator'][entity_key]

    entities_name.reverse()

    for entity_name in entities_name:

        entity = ontology_summary['Class'][entity_name]
        ontology_map[entity_name] = {}
        
        if entity_name in relations_by_domain:

            relations = relations_by_domain[entity_name]
            
            for relation in relations:

                if relation['property'] in ontology_map[entity_name]:
                    relation_descriptor = ontology_map[entity_name][relation['property']]
                else:
                    relation_descriptor = {'targets': []}
                    ontology_map[entity_name][relation['property']] = relation_descriptor

                if relation['property'] in max_cardinality_map[entity_name]:
                    max_cardinality = max_cardinality_map[entity_name][relation['property']]
                    relation_descriptor['max'] = int(max_cardinality)

                if relation['range'] in enumerators_by_entity:
                    enumerators = enumerators_by_entity[relation['range']]
                    for enumerator in enumerators:
                        relation_descriptor['targets'].append(relation['range'] + ':' + enumerator)
                else:
                    relation_descriptor['targets'].append(relation['range'])

                    if relation['range'] in descendants_by_entity:

                        for descendant in descendants_by_entity[relation['range']]:
                            relation_descriptor['targets'].append(descendant)

        if 'parent' in entity and entity['parent'] != 'Thing' and entity['parent'] != 'DataType':

            for entity_property in ontology_map[entity['parent']].keys():
                ontology_map[entity_name][entity_property] = ontology_map[entity['parent']][entity_property]

        if entity_name in enumerators_by_entity:
            enumerators = enumerators_by_entity[entity_name]

            for enumerator in enumerators:
                ontology_map[entity_name+':'+enumerator] = copy(ontology_map[entity_name])

            del ontology_map[entity_name]

    return ontology_map


def get_annotation_guidelines(project_id):

    project = check_project(project_id)

    if 'annotationGuidelines' in project:
        return gridfs.GridFS(db).get(ObjectId(project['annotationGuidelines']['id']))

