import time
import re
import operator
import module.service.documentPackageService as DocumentPackageService
import module.service.userService as UserService
import module.service.nlpService as NlpService
from bson.objectid import ObjectId
from module import db
from module.util.mongoUtil import mongo_result_wrapper
from module.service.serviceException import ServiceException
import tempfile
import zipfile
import uuid
from datetime import datetime, timedelta


def document_result_handler(documents, append_document_package_detail=True, append_collaborator_detail=True,
                            log_document_open=False):

    document_package_map = {}

    for document in documents:

        # document['documentPackageId'] = str(document['documentPackageId'])

        if append_document_package_detail or append_collaborator_detail:

            if document['documentPackageId'] not in document_package_map:
                document_package_map[document['documentPackageId']] = \
                    DocumentPackageService.get_document_package(document['documentPackageId'])
            document['documentPackage'] = document_package_map[document['documentPackageId']]

            if append_collaborator_detail:

                for collaboration in document['collaborations']:
                    user_in_collaborators = any(x['email'] == collaboration['collaborator']
                                                for x in document['documentPackage']['collaborators'])

                    user = {'email': collaboration['collaborator']}

                    if user_in_collaborators:
                        collaboration['collaborator'] = UserService.append_user_details(user)
                    else:
                        collaboration['collaborator'] = user

        if log_document_open:
            db.documents.update({
                '_id': document['id'],
            }, {'$push': {
                'logs': {'firedBy': 'DEFAULT', 'action': 'OPEN', 'atTime': int(time.time())}
            }})

    return documents


def check_document(document_id):

    if not document_id:
        raise ServiceException('INVALID DOCUMENT ID')

    document = get_document(document_id, True, True, False)

    if not document:
        raise ServiceException('INVALID DOCUMENT ID')

    return document


def check_document_package(document_package_id):

    if not document_package_id:
        raise ServiceException('INVALID DOCUMENT PACKAGE ID')

    document_package = DocumentPackageService.get_document_package(document_package_id)

    if not document_package:
        raise ServiceException('INVALID DOCUMENT PACKAGE ID')

    return document_package


def check_document_package_collaborator(document_package_id, collaborator_email):

    document_package = check_document_package(document_package_id)

    if not collaborator_email:
        raise ServiceException('INVALID DOCUMENT PACKAGE COLLABORATOR')

    document_package_collaborator = DocumentPackageService.get_document_package_collaborator(document_package_id,
                                                                                             collaborator_email)

    if not document_package_collaborator:
        raise ServiceException('INVALID DOCUMENT PACKAGE COLLABORATOR')

    collaborator = UserService.get_user(collaborator_email)

    if not collaborator:
        raise ServiceException('INVALID COLLABORATOR')

    return {'collaborator': collaborator, 'document_package': document_package}


@mongo_result_wrapper()
def get_documents(project_id=None, document_package_id=None, status=None, skip=None, limit=None,
                  append_document_package_detail=False, append_collaborator_detail=False, document_package_ids=None):

    match = {}

    if document_package_ids:
        match['documentPackageId'] = {'$in': [ObjectId(v) for v in document_package_ids]}

    elif document_package_id:
        match['documentPackageId'] = ObjectId(document_package_id)

    elif project_id:
        document_packages = DocumentPackageService.get_document_packages_by_project(project_id,
                                                                                    append_document_package_detail,
                                                                                    append_collaborator_detail)
        document_packages_ids = [ObjectId(v['id']) for v in document_packages]

        match['documentPackageId'] = {'$in': document_packages_ids}

    if status:
        match['status'] = status

    query_flow = [
        {'$match': match},
        {'$project': {
            '_id': 0,
            'id': '$_id',
            'documentPackageId': 1,
            'name': 1,
            'metadata': 1,
            'comments': 1,
            'status': 1,
            'text': 1,
            'sentences': 1,
            'tags': 1,
            'relations': 1,
            'logs': 1,
            'collaborations': 1,
            'agreement': 1,
            'stateKey': 1
        }}
    ]

    if skip:
        query_flow.append({'$skip': int(skip)})

    if limit:
        query_flow.append({'$limit': int(limit)})

    return document_result_handler(list(db.documents.aggregate(query_flow)),
                                   append_document_package_detail,
                                   append_collaborator_detail)


@mongo_result_wrapper(is_single_result=True)
def get_document(document_id, append_document_package_detail=True, append_collaborator_detail=True,
                 log_document_open=True):

    result = db.documents.aggregate([
        {'$match': {
            '_id': ObjectId(document_id)
        }},
        {'$project': {
            '_id': 0,
            'id': '$_id',
            'documentPackageId': 1,
            'name': 1,
            'metadata': 1,
            'comments': 1,
            'status': 1,
            'text': 1,
            'sentences': 1,
            'tags': 1,
            'relations': 1,
            'logs': 1,
            'collaborations': 1,
            'agreement': 1,
            'stateKey': 1
        }}
    ])

    return document_result_handler(list(result), append_document_package_detail, append_collaborator_detail,
                                   log_document_open)


def get_documents_zip(document_package_id, include_metadata=True, include_text=True, include_collaboration=True,
                      include_status=True, include_description=True, include_log=True, include_comments=True,
                      wanted_status=['UNCHECKED', 'PRECHECKED', 'CHECKED']):

    documents = get_documents(document_package_id=document_package_id,
                              append_document_package_detail=False, append_collaborator_detail=False)

    zf = zipfile.ZipFile(tempfile.NamedTemporaryFile(delete=False, suffix='.zip'), mode='w')

    temp_dir = tempfile.mkdtemp()

    try:
        for document in documents:

            if document['status'] in wanted_status or len(wanted_status) == 0:

                document_file = get_document_as_file(document, temp_dir + '/' + document['name'],
                                                     include_metadata, include_text,
                                                     include_collaboration, include_status,
                                                     include_description, include_log,
                                                     include_comments)

                zf.write(document_file.name, arcname=document['name'])
    finally:
        zf.close()

    return zf


def get_document_as_file(document, document_path=None, include_metadata=True, include_text=True,
                         include_collaboration=True, include_status=True, include_description=True, include_log=True,
                         include_comments=True):

    try:

        if document_path:
            result_file = open(document_path, 'wb')
        else:
            result_file = tempfile.NamedTemporaryFile(delete=False)

        result_file.write(get_document_as_text(document, include_metadata, include_text,
                                               include_collaboration, include_status,
                                               include_description, include_log,
                                               include_comments).encode('utf-8'))

        result_file.flush()
        result_file.seek(0)

    finally:
        result_file.close()

    return result_file


def get_document_as_text(document, include_metadata=True, include_text=True, include_collaboration=True,
                         include_status=True, include_description=True, include_log=True, include_comments=True):

    # INITIALIZATION

    document_text = ''
    index_by_collaborator = {'#': 0}
    description_header = {'ID': 0, 'FORM': 1}
    next_description_index = 2
    sentence_maps = []

    if include_collaboration:
        for index, collaboration in enumerate(document['collaborations']):
            index_by_collaborator[collaboration['collaborator']] = index + 1

    def get_map(map_type, sentence_key, token_key):
        if map_type not in sentence_maps[sentence_key][token_key]:
            sentence_maps[sentence_key][token_key][map_type] = {}
        return sentence_maps[sentence_key][token_key][map_type]

    def fill_sentence_map(doc, collaborator_email='#', prefix=''):

        collaborator_index = index_by_collaborator[collaborator_email]

        for tag in doc['tags']:
            tag_range = tag['range'].split(':')

            tag_map = get_map('TAG', int(tag_range[0]), int(tag_range[1]))

            label = prefix + 'B|' + tag['label']
            if collaborator_index in tag_map:
                label = tag_map[collaborator_index] + ',' + label

            tag_map[collaborator_index] = label

            for t_index in range(int(tag_range[1]) + 1, int(tag_range[2]) + 1):
                tag_map = get_map('TAG', int(tag_range[0]), t_index)

                label = prefix + 'I|' + tag['label']
                if collaborator_index in tag_map:
                    label = tag_map[collaborator_index] + ',' + label

                tag_map[collaborator_index] = label

        for relation in doc['relations']:
            from_range = relation['from']['range'].split(':')
            to_range = relation['to']['range'].split(':')

            relation_map = get_map('RELATION', int(from_range[0]), int(from_range[1]))

            label = prefix + to_range[0] + '|' + to_range[1] + '|' + relation['label']
            if collaborator_index in relation_map:
                label = relation_map[collaborator_index] + ',' + label

            relation_map[collaborator_index] = label

            for connector in relation['connectors']:
                connector_range = connector.split(':')

                connector_label = from_range[0] + '|' + from_range[1] + '|' + \
                                  to_range[0] + '|' + to_range[1] + '|' + relation['label']

                connector_map = get_map('CONNECTOR', int(connector_range[0]), int(connector_range[1]))

                label = prefix + 'B|' + connector_label
                if collaborator_index in connector_map:
                    label = connector_map[collaborator_index] + ',' + label

                connector_map[collaborator_index] = label

                for t_index in range(int(connector_range[1]) + 1, int(connector_range[2]) + 1):
                    connector_map = get_map('CONNECTOR', int(connector_range[0]), t_index)

                    label = prefix + 'I|' + connector_label
                    if collaborator_index in connector_map:
                        label = connector_map[collaborator_index] + ',' + label

                    connector_map[collaborator_index] = label

    for sentence_index, sentence in enumerate(document['sentences']):
        sentence_map = []
        for token_index, token in enumerate(sentence['tokens']):

            token_map = {'ID': token_index}
            for key, value in token.items():
                if key not in description_header:
                    description_header[key] = next_description_index
                    next_description_index += 1
                token_map[key] = value
            sentence_map.append(token_map)

        sentence_maps.append(sentence_map)

    description_header['TAG'] = next_description_index
    description_header['RELATION'] = next_description_index + 1
    description_header['CONNECTOR'] = next_description_index + 2

    fill_sentence_map(document)

    if include_collaboration:
        for collaboration in document['collaborations']:
            fill_sentence_map(collaboration, collaboration['collaborator'])
            if 'reannotation' in collaboration:
                fill_sentence_map(collaboration['reannotation'], collaboration['collaborator'], 'R|')
            if 'warmUp' in collaboration:
                fill_sentence_map(collaboration['warmUp'], collaboration['collaborator'], 'W|')

    description_header = sorted(description_header.items(), key=operator.itemgetter(1))
    sorted_index_by_collaborator = sorted(index_by_collaborator.items(), key=operator.itemgetter(1))

    # METADATA

    if include_metadata:

        document_text += '\n#METADATA\n'
        for key, value in document['metadata'].items():
            document_text += str(key) + '\t' + str(value) + '\n'

    # TEXT

    if include_text:
        document_text += '\n#TEXT\n' + document['text'] + '\n'

    # COLLABORATORS

    if include_collaboration:
        document_text += '\n#COLLABORATORS\n'
        for index, collaboration in enumerate(document['collaborations']):
            document_text += collaboration['collaborator'] + '\n'

    # STATUS

    if include_status:
        document_text += '\n#STATUS\n'
        document_text += document['status'] + '\n'
        if include_collaboration:
            for index, collaboration in enumerate(document['collaborations']):
                document_text += collaboration['status']
                if 'reannotation' in collaboration:
                    document_text += ',R|' + collaboration['reannotation']['status']
                if 'warmUp' in collaboration:
                    document_text += ',W|' + collaboration['warmUp']['status']
                document_text += '\n'

    # DESCRIPTION

    if include_description:

        document_text += '\n#DESCRIPTION\n'

        # DESCRIPTION HEADER

        for key, value in description_header:
            document_text += str(key) + '\t'
        document_text = document_text[:-1]
        document_text += '\n'

        # DESCRIPTION BODY

        for sentence_map in sentence_maps:
            for token_map in sentence_map:
                for key, value in description_header:

                    if int(value) < next_description_index:
                        if key not in token_map:
                            document_text += 'O'
                        else:
                            document_text += str(token_map[key])
                    else:
                        for collaborator, collaborator_index in sorted_index_by_collaborator:
                            if collaborator_index != 0:
                                document_text += ';'
                            if key not in token_map or collaborator_index not in token_map[key]:
                                document_text += 'O'
                            else:
                                document_text += str(token_map[key][collaborator_index])

                    document_text += '\t'
                document_text += '\n'
            document_text += '\n'

        document_text = document_text[:-1]

    # LOG

    if include_log:

        document_text += '\n#LOG\n'
        document_text += 'TIME\tACTION'

        def get_log_subject_string(subject):
            '''
            if 'subject' in subject:  # 'UNDO/REDO'
                result = ''
                if 'action' in subject:
                    result += subject['action']
                return result + ',' + get_log_subject_string(subject['subject'])
            elif 'action' in subject and subject['action'] == 'MATCH':  # 'MATCH'
                return subject['action']
            '''
            if subject['type'] == 'STATUS': # 'STATUS-CHANGE'
                return subject['type'] + ',' + subject['value']['old'] + '|' + subject['value']['new']
            elif subject['type'] == 'TAG':
                return subject['type'] + ',' + subject['value']['range'].replace(':','|') + '|' + \
                       subject['value']['label']
            elif subject['type'] == 'RELATION':
                from_label = get_log_subject_string({'value': subject['value']['from'], 'type': 'TAG'}).replace('TAG,','')
                to_label = get_log_subject_string({'value': subject['value']['to'], 'type': 'TAG'}).replace('TAG,','')
                return subject['type'] + ',' + from_label + '|' + to_label + '|' + subject['value']['label']
            elif subject['type'] == 'CONNECTOR':
                relation_label = get_log_subject_string({'value': subject['value'], 'type': 'RELATION'})\
                    .replace('RELATION,','')
                return subject['type'] + ',' + relation_label + '|' + subject['value']['range'].replace(':','|')
            elif subject['type'] == 'RANGE':
                return subject['type'] + ',' + subject['value']['range'].replace(':','|')

        def get_log_action_string(action):

            result = '\n'
            if 'atTime' in action:
                result += str(action['atTime']) + '\t'
            else:
                result += '_\t'

            if 'firedBy' in action:
                result += action['firedBy'] + ','

            result += action['action']
            if 'subject' in action and action['action'] not in ['MATCH', 'UNMATCH'] and (
                'type' in action['subject'] or
                ('subject' in action['subject'] and 'type' in action['subject']['subject'])
            ):
                if action['action'] in ['UNDO', 'REDO']:
                    result += ',' + action['subject']['action'] + ',' + \
                              get_log_subject_string(action['subject']['subject'])
                else:
                    result += ',' + get_log_subject_string(action['subject'])
            if 'dependencies' in action:
                for dependency in action['dependencies']:
                    result += get_log_action_string(dependency)

            return result

        def get_document_log_string(doc):
            result = ''
            for log in doc['logs']:
                result += get_log_action_string(log)
            return result

        document_text += get_document_log_string(document)

        if include_collaboration:

            for collaboration in document['collaborations']:

                collaborator_index = index_by_collaborator[collaboration['collaborator']]

                document_text += '\n\n#LOG' + '|' + str(collaborator_index-1) + '\n'
                document_text += 'TIME\tACTION'
                document_text += get_document_log_string(collaboration)

                fill_sentence_map(collaboration, collaboration['collaborator'])
                if 'reannotation' in collaboration:
                    document_text += '\n\n#LOG' + '|' + str(collaborator_index - 1) + '|R\n'
                    document_text += 'TIME\tACTION'
                    document_text += get_document_log_string(collaboration['reannotation'])
                if 'warmUp' in collaboration:
                    document_text += '\n\n#LOG' + '|' + str(collaborator_index - 1) + '|W\n'
                    document_text += 'TIME\tACTION'
                    document_text += get_document_log_string(collaboration['warmUp'])

    # COMMENTS

    if include_comments:

        def get_comments(doc, collaborator_email=None, sufix=None):
            result = '#COMMENTS'
            if collaborator_email:
                result += '|' + str(index_by_collaborator[collaborator_email] - 1)
            if sufix:
                result += '|' + sufix
            result += '\n' + doc['comments']
            return result

        if 'comments' in document and len(document['comments']) > 0:
            document_text += '\n\n' + get_comments(document)

        if include_collaboration:

            for collaboration in document['collaborations']:

                if 'comments' in collaboration and len(collaboration['comments']) > 0:
                    document_text += '\n\n' + get_comments(collaboration, collaboration['collaborator'])

                if 'reannotation' in collaboration:
                    if 'comments' in collaboration['reannotation'] and len(collaboration['reannotation']['comments']) > 0:
                        document_text += '\n\n' + get_comments(collaboration['reannotation'],
                                                               collaboration['collaborator'], 'R')
                if 'warmUp' in collaboration:
                    if 'comments' in collaboration['warmUp'] and len(collaboration['warmUp']['comments']) > 0:
                        document_text += '\n\n' + get_comments(collaboration['warmUp'],
                                                               collaboration['collaborator'], 'W')

    return document_text[1:len(document_text)]


@mongo_result_wrapper(is_insert=True)
def insert_document(document_package_id, document_text, document_name, is_plain_text=False):

    document_package = check_document_package(document_package_id)

    text_filter = {}
    for textReplacement in document_package['project']['textReplacements']:
        text_filter[textReplacement['pattern']] = textReplacement['value']

    document = {
        'name': document_name,
        'metadata': {},
        'text': '',
        'status': 'UNCHECKED',
        'sentences': [],
        'comments': '',
        'tags': [],
        'relations': [],
        'collaborations': [],
        'logs': []
    }

    if is_plain_text:

        document['status'] = 'UNCHECKED'
        document['text'] = document_text

        document['sentences'] = NlpService.get_sentences({'text': document_text,
                                                          'lang': document_package['project']['language'],
                                                          'filter': text_filter,
                                                          'smartSentenceSegmentation': document_package['project']['smartSentenceSegmentation'],
                                                          'smartWordSegmentation': document_package['project']['smartWordSegmentation']})

    else:

        current_section = None
        last_line = None
        has_log = False
        valid_sections = ['#METADATA', '#TEXT', '#COLLABORATORS', '#STATUS', '#DESCRIPTION', '#LOG', '#COMMENTS']

        collaborator_map = {}
        next_collaborator_index = 0
        current_status_index = 0
        current_token_index = 0
        current_sentence_index = -1
        tag_map = {'document': {}}
        relation_map = {'document': {}}
        connector_map = {'document': {}}

        document_text_lines = document_text.splitlines()

        for text_line in document_text_lines:

            if not current_section or (last_line == '' and text_line.startswith('#')):  # HEADER
                if text_line in valid_sections or text_line.startswith('#LOG') or text_line.startswith('#COMMENTS'):

                    if current_section:

                        def get_subject_collaboration(section_title):
                            if section_title.startswith('#LOG') or section_title.startswith('#COMMENTS'):
                                current_section_split = section_title.split('|')
                                if len(current_section_split) == 1:
                                    return document
                                elif len(current_section_split) == 2:
                                    return collaborator_map[int(current_section_split[1])]
                                elif len(current_section_split) == 3:
                                    if current_section_split[2] == 'W':
                                        return collaborator_map[int(current_section_split[1])]['warmUp']
                                    else:
                                        return collaborator_map[int(current_section_split[1])]['reannotation']

                        current_subject_collaboration = get_subject_collaboration(text_line)

                    current_section = text_line

                else:
                    current_section = None
            else: # BODY
                if current_section == '#METADATA' and text_line != '':

                    metadata = text_line.split('\t')
                    document['metadata'][metadata[0]] = metadata[1]

                elif current_section == '#TEXT':

                    text_value = text_line
                    if len(document['text']) > 0:
                        text_value = '\n' + text_line

                    document['text'] += text_value

                elif current_section == '#COLLABORATORS' and text_line != '':

                    collaboration = {
                        'collaborator': text_line,
                        'comments': '',
                        'tags': [],
                        'relations': [],
                        'logs': []
                    }

                    collaborator_map[next_collaborator_index] = collaboration
                    document['collaborations'].append(collaboration)

                    tag_map[next_collaborator_index] = {}
                    relation_map[next_collaborator_index] = {}
                    connector_map[next_collaborator_index] = {}

                    next_collaborator_index += 1

                elif current_section == '#STATUS' and text_line != '':

                    if current_status_index == 0:
                        document['status'] = text_line
                    else:
                        status_list = text_line.split(',')

                        collaboration = collaborator_map[current_status_index-1]
                        collaboration['status'] = status_list[0]

                        if len(status_list) > 0:

                            for status in status_list:

                                status = status.split('|')

                                new_collaboration = {
                                    'status': status[0] if len(status) == 1 else status[1],
                                    'comments': '',
                                    'tags': [],
                                    'relations': [],
                                    'logs': []
                                }

                                if status[0] == 'W':  # warmUp
                                    collaboration['warmUp'] = new_collaboration
                                elif status[0] == 'R':  # reannotation
                                    collaboration['reannotation'] = new_collaboration

                    current_status_index += 1

                elif current_section == '#DESCRIPTION':

                    text_line_split = text_line.split('\t')

                    if text_line == '' or text_line_split[0] == 'ID':
                        current_sentence_index += 1
                        current_token_index = 0
                        current_sentence = {'tokens': []}
                        document['sentences'].append(current_sentence)

                    if text_line_split[0] == 'ID':  # is the header
                        description_header_map = {}
                        for index, text_header in enumerate(text_line_split):
                            description_header_map[text_header] = index

                    elif text_line != '':  # is the body

                        token = {}

                        for header, header_index in description_header_map.items():

                            description_value = text_line_split[header_index]

                            if header not in ['ID','TAG','RELATION','CONNECTOR']:
                                token[header] = description_value
                            elif header in ['TAG','RELATION','CONNECTOR']:
                                description_value_split = description_value.split(';')

                                for collaborator_index, collaboration_text in enumerate(description_value_split):

                                    if collaborator_index == 0:  # document
                                        collaborator_index = 'document'
                                    else:
                                        collaborator_index -= 1

                                    if header == 'TAG':
                                        map_to_use = tag_map[collaborator_index]
                                    elif header == 'RELATION':
                                        map_to_use = relation_map[collaborator_index]
                                    elif header == 'CONNECTOR':
                                        map_to_use = connector_map[collaborator_index]

                                    if current_sentence_index not in map_to_use:
                                        map_to_use[current_sentence_index] = {}

                                    map_to_use[current_sentence_index][current_token_index] = collaboration_text

                        current_sentence['tokens'].append(token)
                        current_token_index += 1

                elif current_section.startswith('#LOG') and text_line != '' and last_line != text_line:
                    if not text_line.startswith('TIME'):

                        has_log = True

                        def text_to_log(text):

                            text_split = text.split('\t')
                            values = text_split[1].split(',')
                            value_index_offset = 0 if text_split[0] != '_' else -1

                            log_to_return = {
                                'dependencies': [],
                                'action': values[1 + value_index_offset]
                            }

                            if text_split[0] != '_':
                                log_to_return['firedBy'] = values[0]
                                log_to_return['atTime'] = int(text_split[0])

                            if len(values) > 2 + value_index_offset:

                                if values[2 + value_index_offset] == 'TAG':
                                    subject_split = values[3 + value_index_offset].split('|')
                                    log_to_return['subject'] = {
                                        'type': 'TAG',
                                        'value': {
                                            'range': subject_split[0] + ':' + subject_split[1] + ':' + subject_split[2],
                                            'label': subject_split[3]
                                        }
                                    }
                                elif values[2 + value_index_offset] == 'RELATION':
                                    subject_split = values[3 + value_index_offset].split('|')
                                    log_to_return['subject'] = {
                                        'type': 'RELATION',
                                        'value': {
                                            'from': {
                                                'range': subject_split[0] + ':' + subject_split[1] + ':' + subject_split[2],
                                                'label': subject_split[3]
                                            },
                                            'to': {
                                                'range': subject_split[4] + ':' + subject_split[5] + ':' + subject_split[6],
                                                'label': subject_split[7]
                                            },
                                            'label': subject_split[8]
                                        }
                                    }
                                elif values[2 + value_index_offset] == 'CONNECTOR':
                                    subject_split = values[3 + value_index_offset].split('|')
                                    log_to_return['subject'] = {
                                        'type': 'CONNECTOR',
                                        'value': {
                                            'from': {
                                                'range': subject_split[0] + ':' + subject_split[1] + ':' + subject_split[2],
                                                'label': subject_split[3]
                                            },
                                            'to': {
                                                'range': subject_split[4] + ':' + subject_split[5] + ':' + subject_split[6],
                                                'label': subject_split[7]
                                            },
                                            'label': subject_split[8],
                                            'range': subject_split[9] + ':' + subject_split[10] + ':' + subject_split[11]
                                        }
                                    }
                                elif values[2 + value_index_offset] == 'RANGE':
                                    subject_split = values[3 + value_index_offset].split('|')
                                    log_to_return['subject'] = {
                                        'type': 'RANGE',
                                        'value': {
                                            'range': subject_split[0] + ':' + subject_split[1] + ':' + subject_split[2]
                                        }
                                    }
                                elif values[2 + value_index_offset] == 'STATUS':
                                    subject_split = values[3 + value_index_offset].split('|')
                                    log_to_return['subject'] = {
                                        'type': 'STATUS',
                                        'value': {
                                            'old': subject_split[0],
                                            'new': subject_split[1]
                                        }
                                    }
                                elif values[1 + value_index_offset] == 'UNDO' or \
                                                values[1 + value_index_offset] == 'REDO':

                                    subject_log = text_to_log(re.sub('UNDO,|REDO,', '', text))

                                    log_to_return['subject'] = {
                                        'action': subject_log['action'],
                                        'subject': subject_log['subject']
                                    }

                            return log_to_return

                        log = text_to_log(text_line)

                        if 'atTime' not in log:
                            last_root_log['dependencies'].append(log)
                            del log['dependencies']
                        else:
                            current_subject_collaboration['logs'].append(log)
                            last_root_log = log

                elif current_section.startswith('#COMMENTS') and text_line != '':
                    comment = text_line
                    if len(current_subject_collaboration['comments']) > 0:
                        comment = '\n' + comment
                    current_subject_collaboration['comments'] += comment

            last_line = text_line

        if has_log:  # if there is log, the log will be used to build tags, relations and connectors

            def build_description_using_log(doc):
                doc_logs = doc['logs']
                doc['logs'] = []
                for log in doc_logs:
                    try:
                        apply_change(doc, log, False)
                        doc['logs'].append(log)
                    except ServiceException as e:
                        pass

            build_description_using_log(document)
            for collaboration in document['collaborations']:
                build_description_using_log(collaboration)
                if 'warmUp' in collaboration:
                    build_description_using_log(collaboration['warmUp'])
                if 'reannotation' in collaboration:
                    build_description_using_log(collaboration['reannotation'])

        else:

            def fill_tags(collaboration_to_fill, collaboration_tag_map):
                for sentence_index, token_map in collaboration_tag_map.items():

                    current_tag = None
                    current_tag_warmup = None
                    current_tag_reannotation = None

                    for token_index, token_description in token_map.items():
                        token_description_split = token_description.split(',')
                        for tag_description in token_description_split:

                            if tag_description != 'O':

                                tag_description_split = tag_description.split('|')

                                if tag_description_split[0] == 'W':
                                    subject_tag = current_tag_warmup
                                    index_offset = 1
                                elif tag_description_split[0] == 'R':
                                    subject_tag = current_tag_reannotation
                                    index_offset = 1
                                else:
                                    subject_tag = current_tag
                                    index_offset = 0

                                if 'B|' in tag_description:
                                    subject_tag = {
                                        'label': tag_description_split[1+index_offset],
                                        'range': str(sentence_index) + ':' + str(token_index) + ':' + str(token_index)
                                    }

                                    if tag_description_split[0] == 'W':
                                        current_tag_warmup = subject_tag
                                        collaboration_to_fill['warmUp']['tags'].append(subject_tag)
                                    elif tag_description_split[0] == 'R':
                                        current_tag_reannotation = subject_tag
                                        collaboration_to_fill['reannotation']['tags'].append(subject_tag)
                                    else:
                                        current_tag = subject_tag
                                        collaboration_to_fill['tags'].append(subject_tag)

                                elif 'I|' in tag_description:
                                    tag_range = subject_tag['range'].split(':')
                                    subject_tag['range'] = tag_range[0] + ':' + \
                                                           tag_range[1] + ':' + str(token_index)

            fill_tags(document, tag_map['document'])
            for collaborator_index, collaboration in collaborator_map.items():
                fill_tags(collaboration, tag_map[collaborator_index])

            tag_by_key = {}

            def fill_tag_by_key(tag, prefix=''):
                tag_range = tag['range'].split(':')
                key = tag_range[0] + '|' + tag_range[1]
                if len(prefix) > 0:
                    key = prefix + '|' + key
                tag_by_key[key] = tag

            for tag in document['tags']:
                fill_tag_by_key(tag)
            for collaborator_index, collaboration in collaborator_map.items():
                for tag in collaboration['tags']:
                    fill_tag_by_key(tag, str(collaborator_index))
                if 'reannotation' in collaboration:
                    for tag in collaboration['reannotation']['tags']:
                        fill_tag_by_key(tag, str(collaborator_index) + '|R')
                if 'warmUp' in collaboration:
                    for tag in collaboration['warmUp']['tags']:
                        fill_tag_by_key(tag, str(collaborator_index) + '|W')

            relation_by_key = {}

            def fill_relations(collaboration_to_fill, collaboration_relation_map, collaborator_index=''):
                for sentence_index, token_map in collaboration_relation_map.items():

                    for token_index, token_description in token_map.items():
                        token_description_split = token_description.split(',')
                        for relation_description in token_description_split:

                            if relation_description != 'O':

                                relation_description_split = relation_description.split('|')

                                if relation_description_split[0] == 'W':
                                    index_offset = 1
                                    key_prefix = str(collaborator_index) + '|W|'

                                elif relation_description_split[0] == 'R':
                                    index_offset = 1
                                    key_prefix = str(collaborator_index) + '|R|'
                                else:
                                    index_offset = 0
                                    key_prefix = ''
                                    if collaborator_index != '':
                                        key_prefix = str(collaborator_index) + '|'

                                to_tag_key = relation_description_split[0+index_offset] + '|' + \
                                             relation_description_split[1+index_offset]

                                from_tag_key = str(sentence_index) + '|' + str(token_index)

                                label = relation_description_split[2+index_offset]
                                relation = {
                                    'label': label,
                                    'from': {
                                        'label': tag_by_key[key_prefix + from_tag_key]['label'],
                                        'range': tag_by_key[key_prefix + from_tag_key]['range']
                                    },
                                    'to': {
                                        'label': tag_by_key[key_prefix + to_tag_key]['label'],
                                        'range': tag_by_key[key_prefix + to_tag_key]['range']
                                    },
                                    'connectors': []
                                }

                                collaboration_to_fill['relations'].append(relation)
                                relation_key = key_prefix + from_tag_key + '|' + to_tag_key + '|' + label
                                relation_by_key[relation_key] = relation

            fill_relations(document, relation_map['document'])
            for collaborator_index, collaboration in collaborator_map.items():
                fill_relations(collaboration, relation_map[collaborator_index], collaborator_index)

            def fill_connectors(collaboration_connector_map, collaborator_index=''):
                for sentence_index, token_map in collaboration_connector_map.items():

                    current_connector = None
                    current_connector_warmup = None
                    current_connector_reannotation = None

                    for token_index, token_description in token_map.items():
                        token_description_split = token_description.split(',')
                        for connector_description in token_description_split:

                            if connector_description != 'O':

                                connector_description_split = connector_description.split('|')

                                if connector_description_split[0] == 'W':
                                    subject_connector = current_connector_warmup
                                    index_offset = 1
                                    key_prefix = str(collaborator_index) + '|W|'
                                elif connector_description_split[0] == 'R':
                                    subject_connector = current_connector_reannotation
                                    index_offset = 1
                                    key_prefix = str(collaborator_index) + '|R|'
                                else:
                                    subject_connector = current_connector
                                    index_offset = 0
                                    key_prefix = ''
                                    if collaborator_index != '':
                                        key_prefix = str(collaborator_index) + '|'

                                if 'B|' in connector_description:

                                    relation_key = key_prefix + \
                                                   connector_description_split[1 + index_offset] + '|' + \
                                                   connector_description_split[2 + index_offset] + '|' + \
                                                   connector_description_split[3 + index_offset] + '|' + \
                                                   connector_description_split[4 + index_offset] + '|' + \
                                                   connector_description_split[5 + index_offset]

                                    relation = relation_by_key[relation_key]

                                    subject_connector = {
                                        'range': str(sentence_index) + ':' + str(token_index) + ':' + str(token_index)
                                    }

                                    if connector_description_split[0] == 'W':
                                        current_connector_warmup = subject_connector
                                        relation['connectors'].append(subject_connector)
                                    elif connector_description_split[0] == 'R':
                                        current_connector_reannotation = subject_connector
                                        relation['connectors'].append(subject_connector)
                                    else:
                                        current_connector = subject_connector
                                        relation['connectors'].append(subject_connector)

                                elif 'I|' in connector_description:
                                    connector_range = subject_connector['range'].split(':')
                                    subject_connector['range'] = connector_range[0] + ':' + \
                                                                 connector_range[1] + ':' + str(token_index)

            fill_connectors(connector_map['document'])
            for collaborator_index, collaboration in collaborator_map.items():
                fill_connectors(connector_map[collaborator_index], collaborator_index)

            # Post processing connectors
            def post_processing_connectors(relation):
                final_connectors = []
                for connector in relation['connectors']:
                    final_connectors.append(connector['range'])
                relation['connectors'] = final_connectors

            for relation in document['relations']:
                post_processing_connectors(relation)
            for collaboration in document['collaborations']:
                for relation in collaboration['relations']:
                    post_processing_connectors(relation)
                if 'reannotation' in collaboration:
                    for relation in collaboration['reannotation']['relations']:
                        post_processing_connectors(relation)
                if 'warmUp' in collaboration:
                    for relation in collaboration['warmUp']['relations']:
                        post_processing_connectors(relation)

        # removing last sentence if is empty
        if len(document['sentences']) > 0:
            last_sentence = document['sentences'].pop()
            if len(last_sentence['tokens']) > 0:
                document['sentences'].append(last_sentence)

        # remove last line of text if is empty
        if document['text'][-1:] == '\n':
            document['text'] = document['text'][:-1]

        if len(document['sentences']) == 0:  # the document doesn't have description

            document['status'] = 'UNCHECKED'
            document['sentences'] = NlpService.get_sentences({'text': document['text'],
                                                              'lang': document_package['project']['language'],
                                                              'filter': text_filter})

            for collaborator in document_package['collaborators']:
                document['collaborations'].append({
                    'collaborator': collaborator['email'],
                    'comments': '',
                    'status': 'UNDONE',
                    'tags': [],
                    'relations': [],
                    'logs': []
                })

    collaboration_by_collaborator = {}
    for collaboration in document['collaborations']:
        collaboration_by_collaborator[collaboration['collaborator']] = collaboration

    for collaborator in document_package['collaborators']:
        if collaborator['email'] not in collaboration_by_collaborator:
            document['collaborations'].append({
                'collaborator': collaborator['email'],
                'comments': '',
                'status': 'UNDONE',
                'tags': [],
                'relations': [],
                'logs': []
            })

    document_id = db.documents.insert_one({
        'documentPackageId': ObjectId(document_package_id),
        'name': document['name'],
        'metadata': document['metadata'],
        'status': document['status'],
        'comments': document['comments'],
        'text': document['text'],
        'sentences': document['sentences'],
        'tags': document['tags'],
        'relations': document['relations'],
        'logs': document['logs'],
        'collaborations': document['collaborations']
    })

    if len(document_package['collaborators']) > 0:
        post_done_check(str(document_id.inserted_id))

    return document_id


def get_document_lock(document_id, collaborator_email=None):

    while True:
        lock_token = str(uuid.uuid4())

        # max lock time is 10 seconds
        limit_time = datetime.now() - timedelta(seconds=10)

        if not collaborator_email:  # document level

            query = {
                '_id': ObjectId(document_id),
                '$or': [
                    {'lockAt': {'$lte': limit_time}},
                    {'lockAt': {'$exists': False}}
                ]
            }
            update = {
                '$set': {
                    'lockAt': datetime.now(),
                    'lockToken': lock_token
                }
            }
        else:  # is collaboration level

            query = {
                '_id': ObjectId(document_id),
                'collaborations.collaborator': collaborator_email,
                '$or': [
                    {'collaborations.lockAt': {'$lte': limit_time}},
                    {'collaborations.lockAt': {'$exists': False}}
                ]
            }

            update = {
                '$set': {
                    'collaborations.$.lockAt': datetime.now(),
                    'collaborations.$.lockToken': lock_token
                }
            }

        result = db.documents.find_and_modify(
            query=query,
            update=update,
            new=True
        )

        if result:  # it's free to lock
            return lock_token

        time.sleep(1)


def release_document_lock(lock_token, document_id, collaborator_email=None):

    if not collaborator_email:  # document level

        query = {
            '_id': ObjectId(document_id),
            'lockToken': lock_token
        }
        update = {
            '$unset': {
                'lockAt': '',
                'lockToken': ''
            }
        }
    else:  # is collaboration level

        query = {
            '_id': ObjectId(document_id),
            'collaborations.collaborator': collaborator_email,
            'collaborations.lockToken': lock_token
        }

        update = {
            '$unset': {
                'collaborations.$.lockAt': '',
                'collaborations.$.lockToken': ''
            }
        }

    db.documents.find_and_modify(
        query=query,
        update=update,
        new=True
    )


def update_document(document_id, name, metadata):

    db.documents.update({
        '_id': ObjectId(document_id)
    }, {
        '$set': {
            'name': name,
            'metadata': metadata
        }
    })


def update_document_by_log(document_id, change_log, lock_token, state_key):

    document = get_document(document_id, False, False, False)

    apply_change(document, change_log)

    new_state_key = str(uuid.uuid4())

    db.documents.update({
        '_id': ObjectId(document_id),
        'lockToken': lock_token,
        '$or': [
            {'stateKey': state_key},
            {'stateKey': {'$exists': False}}
        ]
    }, {
        '$set':{
            'status': document['status'],
            'comments': document['comments'],
            'tags': document['tags'],
            'relations': document['relations'],
            'logs': document['logs'],
            'stateKey': new_state_key
        }
    })

    return new_state_key

    # check_collaborations_status(document_id)


'''
def check_collaborations_status(document_id):

    document = get_document(document_id, False, False, False)

    if document['status'] == 'CHECKED':

        has_collaboration_change = False

        for collaboration in document['collaborations']:

            if collaboration['status'] != 'DONE':
                has_collaboration_change = True
                apply_change(collaboration, {
                    'firedBy': 'SYSTEM', 'action': 'CHANGE', 'atTime': int(time.time()), 'dependencies': [],
                    'subject': {
                        'type': 'STATUS',
                        'value': {
                            'old': collaboration['status'],
                            'new': 'DONE'
                        }
                    }
                })

        if has_collaboration_change:

            db.documents.update({
                '_id': ObjectId(document_id)
            }, {
                '$set': {
                    'name': document['name'],
                    'metadata': document['metadata'],
                    'status': document['status'],
                    'comments': document['comments'],
                    'tags': document['tags'],
                    'relations': document['relations'],
                    'logs': document['logs'],
                    'collaborations': document['collaborations']
                }
            })
'''


def remove_document(document_id):

    db.documents.delete_one({
        '_id': ObjectId(document_id)
    })


def remove_documents_by_document_packages(document_package_ids):

    db.documents.remove({
        'documentPackageId': {'$in': [ObjectId(v) for v in document_package_ids]}
    })


def create_collaborations(document_package_id, collaborator_email):

    check_document_package_collaborator(document_package_id, collaborator_email)

    db.documents.update({
        'documentPackageId': ObjectId(document_package_id),
        'collaborations.collaborator': {'$ne': collaborator_email}
    }, {
        '$push': {
            'collaborations': {
                'collaborator': collaborator_email, 'comments': '',
                'status': 'UNDONE', 'tags': [], 'relations': [], 'logs': []
            }
        }
    }, multi=True)


@mongo_result_wrapper()
def get_collaborations(document_package_id, collaborator_email, document_ids=None, status=None,
                       collaboration_type='DEFAULT'):

    first_match = {'documentPackageId': ObjectId(document_package_id)}
    if document_ids:
        first_match['_id'] = {'$in': [ObjectId(v) for v in document_ids]}

    second_match = {
            'collaborations.collaborator': collaborator_email
    }
    project = {
        '_id': 0,
        'id': '$_id',
        'text': 1,
        'sentences': 1,
        'name': 1,
        'metadata': 1
    }

    if collaboration_type == 'DEFAULT':
        if status:
            second_match['collaborations.status'] = status
        project['status'] = '$collaborations.status'
        project['comments'] = '$collaborations.comments'
        project['tags'] = '$collaborations.tags'
        project['relations'] = '$collaborations.relations'
        project['logs'] = '$collaborations.logs'
        project['reannotation'] = '$collaborations.reannotation'
        project['warmUp'] = '$collaborations.warmUp'
        project['stateKey'] = '$collaborations.stateKey'

    elif collaboration_type == 'REANNOTATION':
        if status:
            second_match['collaborations.reannotation.status'] = status
        project['status'] = '$collaborations.reannotation.status'
        project['comments'] = '$collaborations.reannotation.comments'
        project['tags'] = '$collaborations.reannotation.tags'
        project['relations'] = '$collaborations.reannotation.relations'
        project['logs'] = '$collaborations.reannotation.logs'
        project['stateKey'] = '$collaborations.reannotation.stateKey'

    elif collaboration_type == 'WARMUP':
        if status:
            second_match['collaborations.warmUp.status'] = status
        project['status'] = '$collaborations.warmUp.status'
        project['comments'] = '$collaborations.warmUp.comments'
        project['tags'] = '$collaborations.warmUp.tags'
        project['relations'] = '$collaborations.warmUp.relations'
        project['logs'] = '$collaborations.warmUp.logs'
        project['stateKey'] = '$collaborations.warmUp.stateKey'

    return db.documents.aggregate([
        {'$match': first_match},
        {'$unwind': '$collaborations'},
        {'$match': second_match},
        {'$project': project}
    ])


@mongo_result_wrapper(is_single_result=True)
def get_next_collaboration_to_reannotate(document_package_id, collaborator_email):

    # check_document_package_collaborator(document_package_id, collaborator_email)

    query_flow = [
        {'$match': {'documentPackageId': ObjectId(document_package_id)}},
        {'$unwind': '$collaborations'},
        {'$match': {
            'collaborations.collaborator': collaborator_email,
            'collaborations.status': 'DONE',
            # 'collaborations.reannotation': {'$exists': True},
            'collaborations.reannotation.status': 'UNDONE'
        }},
        {'$project': {
            '_id': 0,
            'id': '$_id',
            'text': 1,
            'sentences': 1,
            'name': 1,
            'metadata': 1,
            'status': '$collaborations.reannotation.status',
            'comments': '$collaborations.reannotation.comments',
            'tags': '$collaborations.reannotation.tags',
            'relations': '$collaborations.reannotation.relations',
            'logs': '$collaborations.reannotation.logs',
            'stateKey': '$collaborations.reannotation.stateKey'
        }}
    ]

    result = list(db.documents.aggregate(query_flow))

    if len(result) > 0:

        db.documents.update({
            '_id': result[0]['id'],
            'documentPackageId': ObjectId(document_package_id),
            'collaborations.collaborator': collaborator_email
        }, {'$push': {
            'collaborations.$.reannotation.logs': {'firedBy': 'DEFAULT', 'action': 'OPEN', 'atTime': int(time.time())}
        }})

        result[0]['type'] = 'reannotation'

    return result


def needs_reannotate(document_package, collaborator_email, statistics=None):

    # check_return = check_document_package_collaborator(document_package, collaborator_email)

    group = DocumentPackageService.get_document_package_group_by_collaborator_email(document_package['id'], collaborator_email)

    if group['reannotationStep'] == 0:
        return False

    if not statistics:
        statistics = DocumentPackageService.get_document_package_collaborator_statistics(document_package['id'],
                                                                                         collaborator_email)

    '''
    # TODO: replace this by statistics
    done_collaborations = get_collaborations(document_package_id, collaborator_email, status='DONE')
    undone_collaborations = get_collaborations(document_package_id, collaborator_email, status='UNDONE')
    done_reannotation_collaborations = get_collaborations(document_package_id, collaborator_email,
                                                          status='DONE', collaboration_type='REANNOTATION')
    '''

    # total_count = statistics['done'] + statistics['undone']

    total_done = statistics['uncheckedDone'] + statistics['precheckedDone'] + statistics['checkedDone']

    expected_done_reannotation_count = int(total_done / group['reannotationStep'])

    return total_done != 0 and \
           total_done % group['reannotationStep'] == 0 and \
           statistics['reannotation'] != expected_done_reannotation_count


def needs_warm_up(document_package, collaborator_email, statistics=None):

    # check_return = check_document_package_collaborator(document_package_id, collaborator_email)

    group = DocumentPackageService.get_document_package_group_by_collaborator_email(document_package['id'], collaborator_email)

    if group['warmUpSize'] == 0:
        return False

    if not statistics:
        statistics = DocumentPackageService.get_document_package_collaborator_statistics(document_package['id'],
                                                                                         collaborator_email)

    '''
    # TODO: replace this by statistics
    done_collaborations = get_collaborations(document_package_id, collaborator_email, status='DONE',
                                             collaboration_type='WARMUP')
    '''

    return statistics['warmUp'] < group['warmUpSize']


@mongo_result_wrapper(is_single_result=True)
def get_random_undone_collaboration(document_package_id, collaborator_email, except_document_id=None):

    document_package = check_document_package(document_package_id)
    statistics = DocumentPackageService.get_document_package_collaborator_statistics(document_package['id'],
                                                                                     collaborator_email)

    if needs_reannotate(document_package, collaborator_email, statistics):
        collaboration = get_next_collaboration_to_reannotate(document_package_id, collaborator_email)
        return collaboration

    def get_random_document(except_id, warm_up):

        match = {
            'documentPackageId': ObjectId(document_package_id),
            'status': 'UNCHECKED'
        }
        if except_id:
            match['_id'] = {'$ne': ObjectId(except_id)}

        query_flow = [
            {'$match': match},
            {'$unwind': "$collaborations"},
            {'$match': {
                'collaborations.collaborator': collaborator_email,
                'collaborations.status': 'UNDONE',
                'collaborations.warmUp': {'$exists': warm_up}
            }},
            {'$project': {
                '_id': 0,
                'id': '$_id',
                'text': 1,
                'sentences': 1,
                'name': 1,
                'metadata': 1,
                'status': '$collaborations.status',
                'comments': '$collaborations.comments',
                'tags': '$collaborations.tags',
                'relations': '$collaborations.relations',
                'logs': '$collaborations.logs',
                'stateKey': '$collaborations.stateKey'
            }},
            {'$sample': {'size': 1}}
        ]

        return list(db.documents.aggregate(query_flow))

    #log_push_key = 'collaborations.$.logs'
    result = get_random_document(except_document_id, False)

    if len(result) == 0:
        result = get_random_document(None, False)

        if len(result) == 0:
            collaborator_needs_warm_up = needs_warm_up(document_package, collaborator_email, statistics)

            # review warm up
            if not collaborator_needs_warm_up:

                #log_push_key = 'collaborations.$.warmUp.logs'
                result = get_random_document(except_document_id, True)

                if len(result) == 0:
                    result = get_random_document(None, True)

                #log_push_key[2]['$match']['collaborations.warmUp'] = {'$exists': True}
                #result = list(db.documents.aggregate(query_flow))

    if len(result) == 1:

        db.documents.update({
            '_id': result[0]['id'],
            'documentPackageId': ObjectId(document_package_id),
            'collaborations.collaborator': collaborator_email
        }, {'$push': {
            'collaborations.$.logs': {'firedBy': 'DEFAULT', 'action': 'OPEN', 'atTime': int(time.time())}
        }})

    return result


def update_collaboration_status(document_id, requester_email, collaborator_email, status):

    lock_token = get_document_lock(document_id, collaborator_email)

    if status not in ['DONE', 'UNDONE']:
        raise ServiceException('INVALID STATUS')

    document = check_document(document_id)

    if document['status'] in ['CHECKED', 'PRECHECKED'] and status == 'UNDONE':
        raise ServiceException('COLLABORATIONS OF CHECKED/PRECHECKED DOCUMENTS CANNOT BE UNDONE')

    if document['documentPackage']['project']['owner'] != requester_email:
        raise ServiceException('ONLY THE ONWER OF PROJECT CAN UPDATE THE STATUS')

    current_collaboration = get_collaborations(document['documentPackage']['id'],
                                               collaborator_email, document_ids=[document_id])[0]

    db.documents.update({
        '_id': ObjectId(document_id),
        'collaborations.collaborator': collaborator_email,
        'collaborations.lockToken': lock_token
    },{
        '$set': {'collaborations.$.status': status},
        '$push': {
            'collaborations.$.logs': {
                'firedBy': 'DEFAULT', 'action': 'CHANGE', 'atTime': int(time.time()), 'dependencies': [],
                'subject': {
                    'type': 'STATUS',
                    'value': {
                        'old': current_collaboration['status'],
                        'new': status
                    }
                }
            }
        }
    })

    release_document_lock(lock_token, document_id, collaborator_email)

    if status == 'DONE':
        post_done_check(document_id)


def apply_change(document, change_log, append_log=True):

    if change_log['action'] in ['CHANGE', 'ADD', 'REMOVE', 'REDO', 'UNDO', 'MATCH', 'UNMATCH']:

        if 'dependencies' in change_log:
            dependencies = change_log['dependencies']
            change_log['dependencies'] = []
            for dependency in dependencies:
                try:
                    apply_change(document, dependency, False)
                    change_log['dependencies'].append(dependency)
                except ServiceException as e:
                    pass

        def get_tag(tag_range, tag_label):
            for tag in document['tags']:
                if tag['range'] == tag_range and tag['label'] == tag_label:
                    return tag

        def get_relation(relation_from, relation_to, relation_label):
            for relation in document['relations']:
                if relation['from']['range'] == relation_from['range'] and \
                   relation['from']['label'] == relation_from['label'] and \
                   relation['to']['range'] == relation_to['range'] and \
                   relation['to']['label'] == relation_to['label'] and \
                   relation['label'] == relation_label:
                    return relation

        if change_log['action'] == 'CHANGE':

            if change_log['subject']['type'] == 'STATUS':
                document['status'] = change_log['subject']['value']['new']

            elif change_log['subject']['type'] == 'COMMENTS':
                document['comments'] = change_log['subject']['value']['new']
                append_log = False

        elif change_log['action'] == 'ADD':

            if change_log['subject']['type'] == 'TAG':

                # checking range
                subject_range = change_log['subject']['value']['range'].split(':')
                for tag in document['tags']:
                    tag_range = tag['range'].split(':')
                    if int(subject_range[0]) == int(tag_range[0]) and (
                                        int(tag_range[1]) <= int(subject_range[1]) <= int(tag_range[2]) or
                                        int(tag_range[1]) <= int(subject_range[2]) <= int(tag_range[2])
                    ):
                        raise ServiceException('INVALID TAG RANGE')

                tag_input = {'label' : change_log['subject']['value']['label'],
                             'range' : change_log['subject']['value']['range']}

                document['tags'].append(tag_input)

            elif change_log['subject']['type'] == 'RELATION':

                from_tag = get_tag(change_log['subject']['value']['from']['range'],
                                   change_log['subject']['value']['from']['label'])

                to_tag = get_tag(change_log['subject']['value']['to']['range'],
                                 change_log['subject']['value']['to']['label'])

                if not from_tag or not to_tag:
                    raise ServiceException('INVALID RELATION')

                relation_input = {
                    'label': change_log['subject']['value']['label'],
                    'connectors': [],
                    'from': from_tag,
                    'to': to_tag
                }

                document['relations'].append(relation_input)

            elif change_log['subject']['type'] == 'CONNECTOR':

                relation = get_relation(change_log['subject']['value']['from'],
                                        change_log['subject']['value']['to'],
                                        change_log['subject']['value']['label'])

                if not relation:
                    raise ServiceException('INVALID CONNECTOR')

                relation['connectors'].append(change_log['subject']['value']['range'])

        elif change_log['action'] == 'REMOVE':

            if change_log['subject']['type'] == 'TAG':

                tag = get_tag(change_log['subject']['value']['range'],
                              change_log['subject']['value']['label'])

                if not tag:
                    raise ServiceException('INVALID TAG REMOVAL')

                document['tags'].remove(tag)

            elif change_log['subject']['type'] == 'RELATION':

                relation = get_relation(change_log['subject']['value']['from'],
                                        change_log['subject']['value']['to'],
                                        change_log['subject']['value']['label'])

                if not relation:
                    raise ServiceException('INVALID RELATION REMOVAL')

                document['relations'].remove(relation)

            elif change_log['subject']['type'] == 'CONNECTOR':

                relation = get_relation(change_log['subject']['value']['from'],
                                        change_log['subject']['value']['to'],
                                        change_log['subject']['value']['label'])

                if not relation:
                    raise ServiceException('INVALID CONNECTOR REMOVAL')

                relation['connectors'].remove(change_log['subject']['value']['range'])

        elif change_log['action'] == 'REDO':
            pass
        elif change_log['action'] == 'UNDO':
            pass
        elif change_log['action'] == 'MATCH' or change_log['action'] == 'UNMATCH':
            pass

        if append_log:
            change_log['atTime'] = int(time.time())
            document['logs'].append(change_log)


def update_collaboration(document_package_id, document_id, collaborator_email, change_log, state_key):

    lock_token = get_document_lock(document_id, collaborator_email)

    document = check_document(document_id)

    '''
    if document['status'] == 'CHECKED':
        raise ServiceException('DOCUMENT ALREADY CHECKED, YOU CANNOT SUBMIT A COLLABORATION')
    '''

    # check_document_package_collaborator(document_package_id, collaborator_email)

    current_collaboration = get_collaborations(document_package_id, collaborator_email, document_ids=[document_id])[0]

    new_state_key = str(uuid.uuid4())

    statistics = DocumentPackageService.get_document_package_collaborator_statistics(document_package_id,
                                                                                     collaborator_email)

    match = {
        '_id': ObjectId(document_id),
        'documentPackageId': ObjectId(document_package_id),
        'collaborations.collaborator': collaborator_email,
        'collaborations.lockToken': lock_token
    }

    if needs_reannotate(document['documentPackage'], collaborator_email, statistics): # reannotation

        if current_collaboration['reannotation']['status'] == 'DONE':
            raise ServiceException('REANNOTATION ALREADY DONE')

        if 'stateKey' in current_collaboration['reannotation'] and \
                        state_key != current_collaboration['reannotation']['stateKey']:
            raise ServiceException('INVALID STATE KEY')

        collaboration_to_reannotate = get_next_collaboration_to_reannotate(document_package_id,
                                                                           collaborator_email)

        if collaboration_to_reannotate['id'] != document_id:
            raise ServiceException('INVALID REANNOTATION DOCUMENT ID')

        apply_change(collaboration_to_reannotate, change_log)

        collaboration_to_reannotate['stateKey'] = new_state_key

        '''db.documents.update(match, {
            '$set': {
                'collaborations.$.reannotation.status': collaboration['status'],
                'collaborations.$.reannotation.tags': collaboration['tags'],
                'collaborations.$.reannotation.relations': collaboration['relations'],
                'collaborations.$.reannotation.logs': collaboration['logs']
            }
        })'''
        db.documents.update(match, {
            '$set': {
                'collaborations.$.reannotation': collaboration_to_reannotate
            }
        })

    else: # warmUp or common collaboration

        if 'stateKey' in current_collaboration and state_key != current_collaboration['stateKey']:
            raise ServiceException('INVALID STATE KEY')

        if change_log['action'] == 'CHANGE' and change_log['subject']['type'] == 'STATUS' and \
           change_log['subject']['value']['new'] == 'DONE' and \
           needs_warm_up(document['documentPackage'], collaborator_email, statistics):

            if 'warmUp' in current_collaboration and  current_collaboration['warmUp']['status'] == 'DONE':
                raise ServiceException('WARMUP ALREADY DONE')

            apply_change(current_collaboration, change_log)

            db.documents.update(match, {
                '$set': {
                    'collaborations.$.comments': '',
                    'collaborations.$.tags': [],
                    'collaborations.$.relations': [],
                    'collaborations.$.logs': [],
                    'collaborations.$.warmUp.status': 'DONE',
                    'collaborations.$.warmUp.comments': current_collaboration['comments'],
                    'collaborations.$.warmUp.tags': current_collaboration['tags'],
                    'collaborations.$.warmUp.relations': current_collaboration['relations'],
                    'collaborations.$.warmUp.logs': current_collaboration['logs'],
                    'collaborations.$.warmUp.stateKey': new_state_key
                }
            })

        else: # common collabotation

            if current_collaboration['status'] == 'DONE':
                raise ServiceException('COLLABOTATION ALREADY DONE')

            apply_change(current_collaboration, change_log)

            current_next_collaboration_to_reannotate = get_next_collaboration_to_reannotate(document_package_id,
                                                                                            collaborator_email)

            if not current_next_collaboration_to_reannotate:
                db.documents.update(match, {'$set': {
                    'collaborations.$.status': current_collaboration['status'],
                    'collaborations.$.comments': current_collaboration['comments'],
                    'collaborations.$.tags': current_collaboration['tags'],
                    'collaborations.$.relations': current_collaboration['relations'],
                    'collaborations.$.logs': current_collaboration['logs'],
                    'collaborations.$.reannotation': {'status': 'UNDONE', 'comments': '',
                                                      'tags': [], 'relations': [], 'logs': []},
                    'collaborations.$.stateKey': new_state_key
                }})
            else:
                db.documents.update(match, {'$set': {
                    'collaborations.$.status': current_collaboration['status'],
                    'collaborations.$.comments': current_collaboration['comments'],
                    'collaborations.$.tags': current_collaboration['tags'],
                    'collaborations.$.relations': current_collaboration['relations'],
                    'collaborations.$.logs': current_collaboration['logs'],
                    'collaborations.$.stateKey': new_state_key
                }})

            if change_log['action'] == 'CHANGE' and change_log['subject']['type'] == 'STATUS' and \
               change_log['subject']['value']['new'] == 'DONE':
                post_done_check(document_id)

            '''
            to_set['collaborations.$.status'] = collaboration['status']
            to_set['collaborations.$.tags'] = collaboration['tags']
            to_set['collaborations.$.relations'] = collaboration['relations']
            to_set['collaborations.$.logs'] = collaboration['logs']

            db.documents.update(match, {'$set': to_set})

            if collaboration['status'] == 'DONE':
                auto_match_document(document_id)
            '''
    release_document_lock(lock_token, document_id, collaborator_email)

    return new_state_key

'''
def auto_match_document(document_id):

    document = get_document(document_id, False, False, False)

    if document['status'] == 'UNCHECKED':

        all_collaborations_done = True

        for collaboration in document['collaborations']:
            if collaboration['status'] == 'UNDONE':
                all_collaborations_done = False
                break

        if all_collaborations_done:

            # creating match log

            log = {'firedBy': 'SYSTEM', 'action': 'MATCH', 'atTime': int(time.time()), 'dependencies': []}

            # creating remove log

            for relation in document['relations']:
                for connector in relation['connectors']:
                    connector_input = {'from': {'label': relation['from']['label'], 'range': relation['from']['range']},
                                       'to': {'label': relation['to']['label'], 'range': relation['to']['range']},
                                       'label': relation['label'], 'range': connector}
                    log['dependencies'].append({'action': 'REMOVE', 'subject': {'type': 'CONNECTOR',
                                                                                'value': connector_input}})

                relation_input = {'from': {'label': relation['from']['label'], 'range': relation['from']['range']},
                                  'to': {'label': relation['to']['label'], 'range': relation['to']['range']},
                                  'label': relation['label']}
                log['dependencies'].append({'action': 'REMOVE', 'subject': {'type': 'RELATION', 'value': relation_input}})

            for tag in document['tags']:
                tag_input = {'label': tag['label'], 'range': tag['range']}
                log['dependencies'].append(
                    {'action': 'REMOVE', 'subject': {'type': 'TAG', 'value': tag_input}})

            # matching

            mapped_tag_wraps = {}
            mapped_relation_wraps = {}
            mapped_connector_wraps = {}

            for collaboration in document['collaborations']:

                for tag in collaboration['tags']:
                    key = tag['label'] + ':' + tag['range']
                    if key not in mapped_tag_wraps:
                        mapped_tag_wraps[key] = {'count':1, 'value':tag}
                    else:
                        mapped_tag_wraps[key]['count'] += 1

                for relation in collaboration['relations']:
                    key = relation['from']['label'] + ':' + relation['from']['range'] \
                          + ':' + relation['to']['label'] + ':' + relation['to']['range'] + ':' + relation['label']

                    if key not in mapped_relation_wraps:
                        mapped_relation_wraps[key] = {'count': 1, 'value': relation}
                    else:
                        mapped_relation_wraps[key]['count'] += 1

                    for connector in relation['connectors']:
                        connector_key = key + ':' + connector

                        if connector_key not in mapped_connector_wraps:
                            mapped_connector_wraps[connector_key] = {'count': 1, 'value': connector, 'relation_key':key}
                        else:
                            mapped_connector_wraps[connector_key]['count'] += 1

            collaborators_count = len(document['collaborations'])

            valid_tags = [v['value'] for k, v in mapped_tag_wraps.items() if v['count'] == collaborators_count]
            invalid_tags = [v['value'] for k, v in mapped_tag_wraps.items() if v['count'] != collaborators_count]

            document['tags'] = valid_tags

            valid_relations = [v['value'] for k, v in mapped_relation_wraps.items()
                               if v['count'] == collaborators_count]
            invalid_relations = [v['value'] for k, v in mapped_relation_wraps.items()
                                 if v['count'] != collaborators_count]

            document['relations'] = valid_relations

            relation_map = {}
            for relation in document['relations']:
                key = relation['from']['label'] + ':' + relation['from']['range'] \
                      + ':' + relation['to']['label'] + ':' + relation['to']['range'] + ':' + relation['label']
                relation['connectors'] = []
                relation_map[key] = relation

            valid_connectors = [v for k, v in mapped_connector_wraps.items() if v['count'] == collaborators_count]
            invalid_connectors = [v for k, v in mapped_connector_wraps.items() if v['count'] != collaborators_count]

            for connector in valid_connectors:
                relation_map[connector['relation_key']]['connectors'].append(connector['value'])

            # creating add log

            for tag in document['tags']:
                tag_input = {'label': tag['label'], 'range': tag['range']}
                log['dependencies'].append(
                    {'action': 'ADD', 'subject': {'type': 'TAG', 'value': tag_input}})

            for relation in document['relations']:
                relation_input = {'from': {'label': relation['from']['label'], 'range': relation['from']['range']},
                                  'to': {'label': relation['to']['label'], 'range': relation['to']['range']},
                                  'label': relation['label']}
                log['dependencies'].append({'action': 'ADD', 'subject': {'type': 'RELATION', 'value': relation_input}})

                for connector in relation['connectors']:
                    connector_input = {'from': {'label': relation['from']['label'], 'range': relation['from']['range']},
                                       'to': {'label': relation['to']['label'], 'range': relation['to']['range']},
                                       'label': relation['label'], 'range': connector}
                    log['dependencies'].append({'action': 'ADD', 'subject': {'type': 'CONNECTOR',
                                                                             'value': connector_input}})

            update_document_by_log(document_id, log)

            # document['logs'].append(log)

            # auto check
            if len(invalid_tags) == 0 and len(invalid_relations) == 0 and len(invalid_connectors) == 0:
                update_document_by_log(document_id, {
                    'firedBy': 'SYSTEM', 'action': 'CHANGE', 'atTime': int(time.time()), 'dependencies': [],
                    'subject': {'type': 'STATUS', 'value': {'old': 'UNCHECKED', 'new': 'CHECKED'} }
                })

            # updating doc
            # update_document(document_id, document)
'''


def auto_match_document(document_id, collaborators_to_use=None):

    lock_token = get_document_lock(document_id)

    document = get_document(document_id, True, False, False)

    # creating match log

    log = {'firedBy': 'SYSTEM', 'action': 'MATCH', 'atTime': int(time.time()), 'dependencies': []}

    # creating remove log

    for relation in document['relations']:
        for connector in relation['connectors']:
            connector_input = {'from': {'label': relation['from']['label'], 'range': relation['from']['range']},
                               'to': {'label': relation['to']['label'], 'range': relation['to']['range']},
                               'label': relation['label'], 'range': connector}
            log['dependencies'].append({'action': 'REMOVE', 'subject': {'type': 'CONNECTOR',
                                                                        'value': connector_input}})

        relation_input = {'from': {'label': relation['from']['label'], 'range': relation['from']['range']},
                          'to': {'label': relation['to']['label'], 'range': relation['to']['range']},
                          'label': relation['label']}
        log['dependencies'].append({'action': 'REMOVE', 'subject': {'type': 'RELATION', 'value': relation_input}})

    for tag in document['tags']:
        tag_input = {'label': tag['label'], 'range': tag['range']}
        log['dependencies'].append(
            {'action': 'REMOVE', 'subject': {'type': 'TAG', 'value': tag_input}})

    # matching

    mapped_tag_wraps = {}
    mapped_relation_wraps = {}
    mapped_connector_wraps = {}
    collaborators_count = 0

    for collaboration in document['collaborations']:

        if not collaborators_to_use or collaboration['collaborator'] in collaborators_to_use:

            collaborators_count += 1

            for tag in collaboration['tags']:
                key = tag['label'] + ':' + tag['range']
                if key not in mapped_tag_wraps:
                    mapped_tag_wraps[key] = {'count':1, 'value':tag}
                else:
                    mapped_tag_wraps[key]['count'] += 1

            for relation in collaboration['relations']:
                key = relation['from']['label'] + ':' + relation['from']['range'] \
                      + ':' + relation['to']['label'] + ':' + relation['to']['range'] + ':' + relation['label']

                if key not in mapped_relation_wraps:
                    mapped_relation_wraps[key] = {'count': 1, 'value': relation}
                else:
                    mapped_relation_wraps[key]['count'] += 1

                for connector in relation['connectors']:
                    connector_key = key + ':' + connector

                    if connector_key not in mapped_connector_wraps:
                        mapped_connector_wraps[connector_key] = {'count': 1, 'value': connector, 'relation_key':key}
                    else:
                        mapped_connector_wraps[connector_key]['count'] += 1

    valid_tags = [v['value'] for k, v in mapped_tag_wraps.items() if v['count'] == collaborators_count]
    invalid_tags = [v['value'] for k, v in mapped_tag_wraps.items() if v['count'] != collaborators_count]

    document['tags'] = valid_tags

    valid_relations = [v['value'] for k, v in mapped_relation_wraps.items()
                       if v['count'] == collaborators_count]
    invalid_relations = [v['value'] for k, v in mapped_relation_wraps.items()
                         if v['count'] != collaborators_count]

    document['relations'] = valid_relations

    relation_map = {}
    for relation in document['relations']:
        key = relation['from']['label'] + ':' + relation['from']['range'] \
              + ':' + relation['to']['label'] + ':' + relation['to']['range'] + ':' + relation['label']
        relation['connectors'] = []
        relation_map[key] = relation

    valid_connectors = [v for k, v in mapped_connector_wraps.items() if v['count'] == collaborators_count]
    invalid_connectors = [v for k, v in mapped_connector_wraps.items() if v['count'] != collaborators_count]

    for connector in valid_connectors:
        relation_map[connector['relation_key']]['connectors'].append(connector['value'])

    # creating add log

    for tag in document['tags']:
        tag_input = {'label': tag['label'], 'range': tag['range']}
        log['dependencies'].append(
            {'action': 'ADD', 'subject': {'type': 'TAG', 'value': tag_input}})

    for relation in document['relations']:
        relation_input = {'from': {'label': relation['from']['label'], 'range': relation['from']['range']},
                          'to': {'label': relation['to']['label'], 'range': relation['to']['range']},
                          'label': relation['label']}
        log['dependencies'].append({'action': 'ADD', 'subject': {'type': 'RELATION', 'value': relation_input}})

        for connector in relation['connectors']:
            connector_input = {'from': {'label': relation['from']['label'], 'range': relation['from']['range']},
                               'to': {'label': relation['to']['label'], 'range': relation['to']['range']},
                               'label': relation['label'], 'range': connector}
            log['dependencies'].append({'action': 'ADD', 'subject': {'type': 'CONNECTOR',
                                                                     'value': connector_input}})

    new_state_key = update_document_by_log(document_id, log, lock_token,
                                           document['stateKey'] if 'stateKey' in document else None)

    # document['logs'].append(log)

    # auto check
    '''
    if len(invalid_tags) == 0 and len(invalid_relations) == 0 and len(invalid_connectors) == 0:
        update_document_by_log(document_id, {
            'firedBy': 'SYSTEM', 'action': 'CHANGE', 'atTime': int(time.time()), 'dependencies': [],
            'subject': {'type': 'STATUS', 'value': {'old': 'UNCHECKED', 'new': 'PRECHECKED'} }
        },lock_token, new_state_key)
    '''

    release_document_lock(lock_token, document_id)

    return new_state_key

    # updating doc
    # update_document(document_id, document)


def post_done_check(document_id):

    lock_token = get_document_lock(document_id)

    document = get_document(document_id, True, False, False)

    best_agreement = None
    all_collaborations_done = True

    for collaboration in document['collaborations']:
        if collaboration['status'] == 'UNDONE':
            all_collaborations_done = False
            break

    if all_collaborations_done or document['documentPackage']['usePrecheckAgreementThreshold']:

        if len(document['collaborations']) > 1:

            agreement_types = []

            if 'useTagAgreement' in document['documentPackage'] and document['documentPackage']['useTagAgreement']:
                agreement_types.append('tag')
            if 'useRelationAgreement' in document['documentPackage'] and document['documentPackage']['useRelationAgreement']:
                agreement_types.append('relation')
            if 'useConnectorAgreement' in document['documentPackage'] and document['documentPackage']['useConnectorAgreement']:
                agreement_types.append('connector')

            if len(agreement_types) == 0:
                agreement_types=['tag', 'relation', 'connector'],

            agreement_statistics = DocumentPackageService.get_document_package_agreement_statistics(
                document['documentPackageId'], agreement_types=agreement_types)

            agreement_ks = []

            for key in agreement_statistics[document_id]['agreement']:

                key_split = key.split(':')

                if len(key_split) == 2 and key_split[0] != key_split[1]:

                    agreement = agreement_statistics[document_id]['agreement'][key]
                    agreement['collaborator1'] = key_split[0]
                    agreement['collaborator2'] = key_split[1]

                    if agreement['collaborator1'] != 'GSA' and agreement['collaborator2'] != 'GSA':
                        agreement_ks.append(agreement['cohenKappa']['k'])
                        if not best_agreement or best_agreement['cohenKappa']['k'] < agreement['cohenKappa']['k']:
                            best_agreement = agreement

            if len(agreement_ks) > 0:
                db.documents.update({
                    '_id': ObjectId(document_id),
                }, {
                    '$set': {
                        'agreement': sum(agreement_ks)/len(agreement_ks)
                    }
                })

        if document['status'] == 'UNCHECKED':

            precheck = True
            if not best_agreement or not document['documentPackage']['usePrecheckAgreementThreshold'] or \
            best_agreement['cohenKappa']['k'] < document['documentPackage']['precheckAgreementThreshold']:
                precheck = False

            if not precheck:
                precheck = True
                for collaboration in document['collaborations']:
                    if collaboration['status'] == 'UNDONE':
                        precheck = False
                        break

            if precheck:

                if best_agreement:
                    document['stateKey'] = auto_match_document(document_id, [best_agreement['collaborator1'],
                                                                            best_agreement['collaborator2']])
                elif len(document['collaborations']) == 1:
                    document['stateKey'] = auto_match_document(document_id, [document['collaborations'][0]['collaborator']])

                lock_token = get_document_lock(document_id)

                update_document_by_log(document_id, {
                    'firedBy': 'SYSTEM', 'action': 'CHANGE', 'atTime': int(time.time()), 'dependencies': [],
                    'subject': {'type': 'STATUS', 'value': {'old': 'UNCHECKED', 'new': 'PRECHECKED'}}
                }, lock_token, document['stateKey'] if 'stateKey' in document else None)

    release_document_lock(lock_token, document_id)
