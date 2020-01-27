import copy

import module.service.projectService as ProjectService
import module.service.userService as UserService
import module.util.objectUtil as ObjectUtil
import module.util.statistics as Statistics
from bson.objectid import ObjectId
from module import db
from module.util.mongoUtil import mongo_result_wrapper
from module.service.serviceException import ServiceException
import time
import statistics
from operator import itemgetter


def document_package_result_handler(document_packages, append_project_detail, append_collaborator_detail,
                                    append_statistics):

    for document_package in document_packages:

        groups_map = {}

        for group in document_package['groups']:
            groups_map[group['id']] = group

        if append_project_detail:
            document_package['project'] = ProjectService.get_project(document_package['projectId'])
            del document_package['projectId']

        if append_collaborator_detail:
            for collaborator in document_package['collaborators']:
                UserService.append_user_details(collaborator)
                collaborator['group'] = groups_map[collaborator['groupId']]

        if append_statistics:
            document_package['statistics'] = get_document_package_status_statistics(document_package['id'])

    return document_packages


@mongo_result_wrapper(is_single_result=True)
def get_document_package(document_package_id, append_project_detail=True, append_collaborator_detail=True,
                         append_statistics=False):

    result = db.documentPackages.aggregate([
        {'$match': {
            '_id': ObjectId(document_package_id)
        }},
        {'$project': {
            '_id': 0,
            'id': '$_id',
            'name': 1,
            'projectId': 1,
            'groups': 1,
            'collaborators': 1,
            'randomAnnotation': 1,
            'showSelfAgreementFeedback': 1,
            'selfAgreementFeedbackGoal': 1,
            'usePrecheckAgreementThreshold': 1,
            'precheckAgreementThreshold': 1,
            'useTagAgreement': 1,
            'useRelationAgreement': 1,
            'useConnectorAgreement': 1
        }}
    ])

    return document_package_result_handler(list(result), append_project_detail, append_collaborator_detail,
                                           append_statistics)


@mongo_result_wrapper()
def get_document_packages(document_package_ids=None, append_project_detail=True, append_collaborator_detail=True,
                          skip=None, limit=None, append_statistics=False):

    match = {}

    if document_package_ids and len(document_package_ids) > 0:
        document_package_ids = [ObjectId(v) for v in document_package_ids]
        match['_id'] = {"$in": document_package_ids}

    query_flow = [
        {'$match': match},
        {'$project': {
            '_id': 0,
            'id': '$_id',
            'name': 1,
            'projectId': 1,
            'groups': 1,
            'collaborators': 1,
            'randomAnnotation': 1,
            'showSelfAgreementFeedback': 1,
            'selfAgreementFeedbackGoal': 1,
            'usePrecheckAgreementThreshold': 1,
            'precheckAgreementThreshold': 1,
            'useTagAgreement': 1,
            'useRelationAgreement': 1,
            'useConnectorAgreement': 1
        }}]

    if skip:
        query_flow.append({'$skip': int(skip)})

    if limit:
        query_flow.append({'$limit': int(limit)})

    result = db.documentPackages.aggregate(query_flow)

    return document_package_result_handler(list(result), append_project_detail, append_collaborator_detail,
                                           append_statistics)


@mongo_result_wrapper()
def get_document_packages_by_project(project_id, append_project_detail=True, append_collaborator_detail=True,
                                     append_statistics=False):

    result = db.documentPackages.aggregate([
        {'$match': {
            'projectId': ObjectId(project_id)
        }},
        {'$project': {
            '_id': 0,
            'id': '$_id',
            'name': 1,
            'projectId': 1,
            'groups': 1,
            'collaborators': 1,
            'randomAnnotation': 1,
            'showSelfAgreementFeedback': 1,
            'selfAgreementFeedbackGoal': 1,
            'usePrecheckAgreementThreshold': 1,
            'precheckAgreementThreshold': 1,
            'useTagAgreement': 1,
            'useRelationAgreement': 1,
            'useConnectorAgreement': 1
        }}
    ])

    return document_package_result_handler(list(result), append_project_detail, append_collaborator_detail,
                                           append_statistics)


@mongo_result_wrapper(is_insert=True)
def create_document_package(project_id, name, random_annotation=False, show_self_agreement_feedback=False, self_agreement_feedback_goal=None,
                            use_precheck_agreement_threshold=False, precheck_agreement_threshold=1,
                            use_tag_agreement=True, use_relation_agreement=True, use_connector_agreement=True):

    project = ProjectService.get_project(project_id)

    if not project:
        raise ServiceException('INVALID PROJECT_ID')

    return db.documentPackages.insert_one({
        'name': name,
        'projectId': ObjectId(project_id),
        'groupSequence': 0,
        'groups': [
            {'id': 0, 'name': 'DEFAULT', 'warmUpSize': 0, 'reannotationStep': 0}
        ],
        'collaborators': [],
        'randomAnnotation': random_annotation,
        'showSelfAgreementFeedback': show_self_agreement_feedback,
        'selfAgreementFeedbackGoal': self_agreement_feedback_goal,
        'usePrecheckAgreementThreshold': use_precheck_agreement_threshold,
        'precheckAgreementThreshold': precheck_agreement_threshold,
        'useTagAgreement': use_tag_agreement,
        'useRelationAgreement': use_relation_agreement,
        'useConnectorAgreement': use_connector_agreement
    })


def update_document_package(document_package_id, name, random_annotation=False, show_self_agreement_feedback=False, self_agreement_feedback_goal=None,
                            use_precheck_agreement_threshold=False, precheck_agreement_threshold=1, use_tag_agreement=True,
                            use_relation_agreement=True, use_connector_agreement=True):

    db.documentPackages.update({
        '_id': ObjectId(document_package_id)
    }, {
        '$set': {
            'name': name,
            'randomAnnotation': random_annotation,
            'showSelfAgreementFeedback': show_self_agreement_feedback,
            'selfAgreementFeedbackGoal': self_agreement_feedback_goal,
            'usePrecheckAgreementThreshold': use_precheck_agreement_threshold,
            'precheckAgreementThreshold': precheck_agreement_threshold,
            'useTagAgreement': use_tag_agreement,
            'useRelationAgreement': use_relation_agreement,
            'useConnectorAgreement': use_connector_agreement
        }
    })


def remove_document_package(document_package_id):

    import module.service.documentService as DocumentService
    DocumentService.remove_documents_by_document_packages([document_package_id])

    db.documentPackages.delete_one({
        '_id': ObjectId(document_package_id)
    })


def remove_document_package_by_project(project_id):

    document_packages = get_document_packages_by_project(project_id, False, False)

    import module.service.documentService as DocumentService
    DocumentService.remove_documents_by_document_packages([v['id'] for v in document_packages])

    db.documentPackages.remove({
        'projectId': ObjectId(project_id)
    })


def insert_document_package_group(document_package_id, name, warm_up_size=0, reannotation_step=0):

    statistics = get_document_package_status_statistics(document_package_id)
    total = statistics['checked'] + statistics['unchecked']

    if warm_up_size > total:
        raise ServiceException('WARM UP CANNOT BE HIGHER THAN DOCUMENTS SIZE')

    if reannotation_step > total:
        raise ServiceException('REANNOTATION STEP CANNOT BE HIGHER THAN DOCUMENTS SIZE')

    result = db.documentPackages.find_and_modify(
        query = {'_id': ObjectId(document_package_id)},
        update = {
            '$inc': {'groupSequence': 1}
        },
        new = True
    )

    db.documentPackages.update({
        '_id': ObjectId(document_package_id)
    }, {
        '$addToSet': {
            'groups': {
                'id': result['groupSequence'],
                'name': name,
                'warmUpSize': warm_up_size,
                'reannotationStep': reannotation_step
            }
        }
    })

    return result['groupSequence']


def update_document_package_group(document_package_id, group_id, name, warm_up_size=0, reannotation_step=0):

    if group_id == 0:
        raise ServiceException('CANNOT UPDATE DEFAULT GROUP')

    statistics = get_document_package_status_statistics(document_package_id)
    total = statistics['checked'] + statistics['unchecked']

    if warm_up_size > total:
        raise ServiceException('WARM UP CANNOT BE HIGHER THAN DOCUMENTS SIZE')

    if reannotation_step > total:
        raise ServiceException('REANNOTATION STEP CANNOT BE HIGHER THAN DOCUMENTS SIZE')

    db.documentPackages.update({
        '_id': ObjectId(document_package_id),
        'groups.id': group_id
    }, {
        '$set': {
            'groups.$.name': name,
            'groups.$.warmUpSize': warm_up_size,
            'groups.$.reannotationStep': reannotation_step
        }
    })


def remove_document_package_group(document_package_id, group_id):

    if group_id == 0:
        raise ServiceException('CANNOT REMOVE DEFAULT GROUP')

    db.documentPackages.update({
        '_id': ObjectId(document_package_id),
        'collaborators.groupId': group_id
    }, {
        '$set': {
            'collaborators.$.groupId': 0
        }
    })

    db.documentPackages.update({
        '_id': ObjectId(document_package_id),
    }, {
        '$pull': {
            'groups': {
                'id': group_id
            }
        }
    })


@mongo_result_wrapper(is_single_result=True)
def get_document_package_group(document_package_id, group_id):

    return db.documentPackages.aggregate([
        {'$unwind': '$groups'},
        {'$match': {
            '_id': ObjectId(document_package_id),
            'groups.id': group_id
        }},
        {'$project': {
            'id': '$groups.id',
            'name': '$groups.name',
            'warmUpSize': '$groups.warmUpSize',
            'reannotationStep': '$groups.reannotationStep'
        }}
    ])


@mongo_result_wrapper()
def get_document_package_groups(document_package_id):

    return db.documentPackages.aggregate([
        {'$unwind': '$groups'},
        {'$match': {
            '_id': ObjectId(document_package_id)
        }},
        {'$project': {
            'id': '$groups.id',
            'name': '$groups.name',
            'warmUpSize': '$groups.warmUpSize',
            'reannotationStep': '$groups.reannotationStep'
        }}
    ])


def get_document_package_group_by_collaborator_email(document_package_id, collaborator_email):

    document_package = get_document_package(document_package_id, append_project_detail=False,
                                            append_collaborator_detail=True)

    for collaborator in document_package['collaborators']:
        if collaborator['email'] == collaborator_email:
            return collaborator['group']


def insert_document_package_collaborator(document_package_id, group_id, collaborator_email):

    if not collaborator_email:
        raise ServiceException('COLLABORATOR EMAIL CANNOT BE NULL')

    collaborator = get_document_package_collaborator(document_package_id, collaborator_email)

    if collaborator:
        raise ServiceException('COLLABORATOR ALREADY EXISTS')

    user = UserService.get_user(collaborator_email)

    if not user:
        raise ServiceException('INVALID COLLABORATOR EMAIL')

    db.documentPackages.update({
        '_id': ObjectId(document_package_id)
    }, {
        '$addToSet': {
            'collaborators': {
                'groupId': group_id,
                'email': collaborator_email
            }
        }
    })

    import module.service.documentService as DocumentService
    DocumentService.create_collaborations(document_package_id, collaborator_email)


def update_document_package_collaborator(document_package_id, group_id, collaborator_email):

    collaborator = get_document_package_collaborator(document_package_id, collaborator_email)

    if not collaborator:
        raise ServiceException('INVALID COLLABORATOR')

    db.documentPackages.update({
        '_id': ObjectId(document_package_id),
        'collaborators.email': collaborator_email
    }, {
        '$set': {
            'collaborators.$.groupId': group_id
        }
    })


@mongo_result_wrapper(is_single_result=True)
def get_document_package_collaborator(document_package_id, collaborator_email):

    return db.documentPackages.aggregate([
        {'$unwind': "$collaborators"},
        {'$match': {
            '_id': ObjectId(document_package_id),
            'collaborators.email': collaborator_email
        }},
        {'$project': {
            'email': '$collaborators.email'
        }}
    ])


@mongo_result_wrapper()
def get_document_package_collaborators(document_package_id):

    return db.documentPackages.aggregate([
        {'$unwind': "$collaborators"},
        {'$match': {
            '_id': ObjectId(document_package_id)
        }},
        {'$project': {
            'email': '$collaborators.email'
        }}
    ])


def remove_document_package_collaborator(document_package_id, collaborator_email):

    db.documentPackages.update({
        '_id': ObjectId(document_package_id),
    }, {
        '$pull': {
            'collaborators': {
                'email': collaborator_email
            }
        }
    })


@mongo_result_wrapper()
def get_document_packages_by_collaborator(collaborator_email, append_project_detail=True,
                                          append_collaborator_detail=True, append_statistics=False):

    result = list(db.documentPackages.aggregate([
        {'$match': {
            'collaborators.email': collaborator_email
        }},
        {'$project': {
            '_id': 0,
            'id': '$_id',
            'name': 1,
            'projectId': 1,
            'groups': 1,
            'collaborators': 1,
            'randomAnnotation': 1,
            'showSelfAgreementFeedback': 1,
            'selfAgreementFeedbackGoal': 1,
            'usePrecheckAgreementThreshold': 1,
            'precheckAgreementThreshold': 1,
            'useTagAgreement': 1,
            'useRelationAgreement': 1,
            'useConnectorAgreement': 1
        }}
    ]))

    return document_package_result_handler(result, append_project_detail, append_collaborator_detail,
                                           append_statistics)


@mongo_result_wrapper()
def get_document_package_comments(document_package_id):

    return db.documents.aggregate([
        { '$match': {'documentPackageId': ObjectId(document_package_id)}},
        { '$project': {
            '_id': 0,
            'id': '$_id',
            'name': 1,
            'collaborations': {'$filter': {
                'input': '$collaborations',
                'as': 'collaboration',
                'cond': {'$ne': ['$$collaboration.comments', '']}
            }}
        }},
        { '$match': {'collaborations': {'$not': {'$size': 0}}}},
        { '$project': {
            'id': 1,
            'name': 1,
            'collaborations.collaborator': 1,
            'collaborations.comments': 1
        }},
    ])

'''
def get_document_package_statistics(document_package_id, is_full=False, collaborators_to_filter=None):

    if not is_full:

        result = list(db.documents.aggregate([
            {'$match': {
                'documentPackageId': ObjectId(document_package_id)
            }},
            {'$project': {
                'checked': {
                    '$cond': {
                        'if': {'$eq': ['$status', 'CHECKED']},
                        'then': 1, 'else': 0
                    }
                },
                'prechecked': {
                    '$cond': {
                        'if': {'$eq': ['$status', 'PRECHECKED']},
                        'then': 1, 'else': 0
                    }
                },
                'unchecked': {
                    '$cond': {
                        'if': {'$eq': ['$status', 'UNCHECKED']},
                        'then': 1, 'else': 0
                    }
                }
            }},
            {'$group': {
                '_id': '$documentPackageId',
                'checked': {'$sum': '$checked'},
                'prechecked': {'$sum': '$prechecked'},
                'unchecked': {'$sum': '$unchecked'}
            }},
            {'$project': {
                '_id': 0,
                'checked': 1,
                'prechecked': 1,
                'unchecked': 1
            }}
        ]))

        if len(result) > 0:
            return result[0]
        else:
            return {'checked': 0, 'prechecked': 0, 'unchecked': 0}

    else:

        result = {'tags': {}, 'relations': {}, 'connectors': {},
                  'coverage': {'empty': 0, 'tag': 0, 'connector': 0},
                  'checked': 0, 'prechecked': 0, 'unchecked': 0, 'collaborations': {}, 'documents': []}

        def fill_statistics(document, result_to_fill):

            document_log = {'name': document['name'], 'id': document['id']}
            if 'agreement' in document:
                document_log['agreement'] = document['agreement']

            result_to_fill['documents'].append(document_log)
            time_spent = 0
            number_of_views = 0
            previous_action = None

            for action in document['logs']:
                if action['action'] == 'CHANGE' and action['subject']['type'] == 'STATUS' and \
                                action['subject']['value']['new'] == 'DONE':
                    document_log['doneAt'] = action['atTime']

                if action['action'] == 'OPEN':
                    previous_action = action
                    number_of_views += 1
                    continue
                elif action['action'] == 'CHANGE' and action['subject']['type'] == 'STATUS' and \
                     action['subject']['value']['new'] == 'UNDONE':
                    previous_action = None
                    continue
                elif previous_action:
                    time_spent += action['atTime'] - previous_action['atTime']
                previous_action = action

            document_log['timeSpent'] = time_spent
            document_log['numberOfViews'] = number_of_views

            if document['status'] == 'CHECKED':
                result_to_fill['checked'] += 1
            if document['status'] == 'PRECHECKED':
                result_to_fill['prechecked'] += 1
            elif document['status'] == 'UNCHECKED':
                result_to_fill['unchecked'] += 1
            elif document['status'] == 'DONE':
                result_to_fill['done'] += 1
            elif document['status'] == 'UNDONE':
                result_to_fill['undone'] += 1

            for sentence in document['sentences']:
                result_to_fill['coverage']['empty'] += len(sentence['tokens'])

            for tag in document['tags']:

                tag_range = tag['range'].split(':')
                coverage = abs(int(tag_range[1]) - int(tag_range[2])) + 1
                result_to_fill['coverage']['tag'] += coverage
                result_to_fill['coverage']['empty'] -= coverage

                if tag['label'] not in result_to_fill['tags']:
                    result_to_fill['tags'][tag['label']] = 1
                else:
                    result_to_fill['tags'][tag['label']] += 1

            for relation in document['relations']:
                if relation['label'] not in result_to_fill['relations']:
                    result_to_fill['relations'][relation['label']] = 1
                else:
                    result_to_fill['relations'][relation['label']] += 1
                if len(relation['connectors']) > 0:

                    for connector in relation['connectors']:
                        connector_range = connector.split(':')
                        coverage = abs(int(connector_range[1]) - int(connector_range[2])) + 1
                        result_to_fill['coverage']['connector'] += coverage
                        result_to_fill['coverage']['empty'] -= coverage

                    if relation['label'] not in result_to_fill['connectors']:
                        result_to_fill['connectors'][relation['label']] = len(relation['connectors'])
                    else:
                        result_to_fill['connectors'][relation['label']] += len(relation['connectors'])

        import module.service.documentService as DocumentService
        documents = DocumentService.get_documents(document_package_id=document_package_id)

        for doc in documents:
            fill_statistics(doc, result)

            for collaboration in doc['collaborations']:

                if not collaborators_to_filter or collaboration['collaborator'] in collaborators_to_filter:

                    if collaboration['collaborator'] not in result['collaborations']:
                        result['collaborations'][collaboration['collaborator']] = {'tags': {}, 'relations': {},
                                                                                   'connectors': {},
                                                                                   'coverage': {'empty': 0,
                                                                                                'tag': 0,
                                                                                                'connector': 0},
                                                                                   'done': 0, 'undone': 0,
                                                                                   'documents': []}

                    collaboration['id'] = doc['id']
                    collaboration['documentPackageId'] = doc['documentPackageId']
                    collaboration['name'] = doc['name']
                    collaboration['sentences'] = doc['sentences']
                    fill_statistics(collaboration, result['collaborations'][collaboration['collaborator']])

        # AGREEMENTS
        result['agreements'] = {'package': None, 'documents': []}

        groups_map = get_groups_map(documents)

        agreements = {
            'all': get_agreement_statistics(documents, collaborators_to_filter, groups_map, 'all'),
            'tag': get_agreement_statistics(documents, collaborators_to_filter, groups_map, 'tag'),
            'relation': get_agreement_statistics(documents, collaborators_to_filter, groups_map, 'relation'),
            'connector': get_agreement_statistics(documents, collaborators_to_filter, groups_map, 'connector')
        }
        result['agreements']['package']= agreements

        for doc in documents:

            agreements = {
                'all': get_agreement_statistics([doc], collaborators_to_filter, groups_map, 'all'),
                'tag': get_agreement_statistics([doc], collaborators_to_filter, groups_map, 'tag'),
                'relation': get_agreement_statistics([doc], collaborators_to_filter, groups_map, 'relation'),
                'connector': get_agreement_statistics([doc], collaborators_to_filter, groups_map, 'connector')
            }
            result['agreements']['documents'].append({
                'id': doc['id'],
                'agreement': agreements
            })

        return result

'''

'''
def get_groups_map(documents):

    groups_map = {}
    for doc in documents:
        document_package_id = doc['documentPackageId']
        if document_package_id not in groups_map:
            groups_map[document_package_id] = {}
        for collaboration in doc['collaborations']:
            collaborator_email = collaboration['collaborator']
            if collaborator_email not in groups_map[document_package_id]:
                collaborator_group = get_document_package_group_by_collaborator_email(document_package_id,
                                                                                      collaborator_email)
                groups_map[document_package_id][collaborator_email] = collaborator_group
    return groups_map
'''

def get_document_package_collaborators_statistics(document_package_id, collaborator_emails=None):

    second_match = {}
    if collaborator_emails and len(collaborator_emails) > 0:
        second_match = {
            'collaborations.collaborator': {'$in': collaborator_emails}
        }

    return list(db.documents.aggregate([
        {'$match': {
            'documentPackageId': ObjectId(document_package_id)
        }},
        {'$unwind': "$collaborations"},
        {'$match': second_match},
        {'$project': {
            '_id': 0,
            'collaborator': '$collaborations.collaborator',
            'uncheckedDone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'UNCHECKED']},
                            {'$eq': ['$collaborations.status', 'DONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'checkedDone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'CHECKED']},
                            {'$eq': ['$collaborations.status', 'DONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'precheckedDone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'PRECHECKED']},
                            {'$eq': ['$collaborations.status', 'DONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'uncheckedUndone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'UNCHECKED']},
                            {'$eq': ['$collaborations.status', 'UNDONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'checkedUndone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'CHECKED']},
                            {'$eq': ['$collaborations.status', 'UNDONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'precheckedUndone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'PRECHECKED']},
                            {'$eq': ['$collaborations.status', 'UNDONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'reannotation': {
                '$cond': {
                    'if': {'$eq': ['$collaborations.reannotation.status', 'DONE']},
                    'then': 1, 'else': 0
                }
            },
            'warmUp': {
                '$cond': {
                    'if': {'$eq': ['$collaborations.warmUp.status', 'DONE']},
                    'then': 1, 'else': 0
                }
            }
        }},
        {'$group': {
            '_id': {
                'collaborator': '$collaborator'
            },
            'checkedDone': {'$sum': '$checkedDone'},
            'precheckedDone': {'$sum': '$precheckedDone'},
            'uncheckedDone': {'$sum': '$uncheckedDone'},
            'checkedUndone': {'$sum': '$checkedUndone'},
            'precheckedUndone': {'$sum': '$precheckedUndone'},
            'uncheckedUndone': {'$sum': '$uncheckedUndone'},
            'reannotation': {'$sum': '$reannotation'},
            'warmUp': {'$sum': '$warmUp'}
        }},
        {'$project': {
            '_id': 0,
            'collaborator': '$_id.collaborator',
            'checkedDone': 1,
            'precheckedDone': 1,
            'uncheckedDone': 1,
            'checkedUndone': 1,
            'precheckedUndone': 1,
            'uncheckedUndone': 1,
            'reannotation': 1,
            'warmUp': 1
        }}
    ]))


def get_document_package_collaborator_statistics(document_package_id, collaborator_email, append_agreement=False):

    result = list(db.documents.aggregate([
        {'$match': {
            'documentPackageId': ObjectId(document_package_id)
        }},
        {'$unwind': "$collaborations"},
        {'$match': {
            'collaborations.collaborator': collaborator_email
        }},
        {'$project': {
            '_id': 0,
            'collaborator': '$collaborations.collaborator',
            'uncheckedDone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'UNCHECKED']},
                            {'$eq': ['$collaborations.status', 'DONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'checkedDone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'CHECKED']},
                            {'$eq': ['$collaborations.status', 'DONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'precheckedDone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'PRECHECKED']},
                            {'$eq': ['$collaborations.status', 'DONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'uncheckedUndone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'UNCHECKED']},
                            {'$eq': ['$collaborations.status', 'UNDONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'checkedUndone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'CHECKED']},
                            {'$eq': ['$collaborations.status', 'UNDONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'precheckedUnDone': {
                '$cond': {
                    'if': {
                        '$and': [
                            {'$eq': ['$status', 'PRECHECKED']},
                            {'$eq': ['$collaborations.status', 'UNDONE']}
                        ]
                    },
                    'then': 1, 'else': 0
                }
            },
            'reannotation': {
                '$cond': {
                    'if': {'$eq': ['$collaborations.reannotation.status', 'DONE']},
                    'then': 1, 'else': 0
                }
            },
            'warmUp': {
                '$cond': {
                    'if': {'$eq': ['$collaborations.warmUp.status', 'DONE']},
                    'then': 1, 'else': 0
                }
            }
        }},
        {'$group': {
            '_id': {
                'collaborator': '$collaborator'
            },
            'checkedDone': {'$sum': '$checkedDone'},
            'precheckedDone': {'$sum': '$precheckedDone'},
            'uncheckedDone': {'$sum': '$uncheckedDone'},
            'checkedUndone': {'$sum': '$checkedUndone'},
            'precheckedUndone': {'$sum': '$precheckedUndone'},
            'uncheckedUndone': {'$sum': '$uncheckedUndone'},
            'reannotation': {'$sum': '$reannotation'},
            'warmUp': {'$sum': '$warmUp'}
        }},
        {'$project': {
            '_id': 0, 
            'checkedDone': 1, 
            'precheckedDone': 1,
            'uncheckedDone': 1,
            'checkedUndone': 1,
            'precheckedUndone': 1,
            'uncheckedUndone': 1,
            'reannotation': 1, 
            'warmUp': 1
        }}
    ]))

    if len(result) > 0:
        stats = result[0]
    else:
        stats = {
            'checkedDone': 0, 
            'precheckedDone': 0,
            'uncheckedDone': 0,
            'checkedUndone': 0,
            'precheckedUndone': 0,
            'uncheckedUndone': 0,
            'reannotation': 0, 
            'warmUp': 0
        }
    
    if append_agreement:

        document_package_summary = get_document_package_summary_statistics(document_package_id, include_collaborations=True, collaborators_to_filter=[collaborator_email])        
        done_at_by_id = {}

        for summary in document_package_summary:

            id = summary['id']
            done_at = summary['collaborations'][collaborator_email]['doneAt']

            done_at_by_id[id] = done_at

        agreement = get_document_package_agreement_statistics(document_package_id, collaborators_to_filter=[collaborator_email])
        self_agreement = []
        self_agreement_key = collaborator_email + ':' + collaborator_email

        for id in done_at_by_id:
            collaboration_agreement = agreement[id]['agreement']
            if self_agreement_key in collaboration_agreement:
                self_agreement.append({
                    'cohenKappa': collaboration_agreement[self_agreement_key]['cohenKappa'],
                    'id': id,
                    'doneAt': done_at_by_id[id]
                })

        self_agreement.sort(key=itemgetter('doneAt'))
        stats['selfAgreement'] = self_agreement

    return stats


def change_documents_status(document_package_id, new_status):

    import module.service.documentService as DocumentService
    documents = DocumentService.get_documents(document_package_id=document_package_id)

    for document in documents:
        if document['status'] != new_status:
            change_log = {
                'firedBy': 'DEFAULT', 'action': 'CHANGE', 'atTime': int(time.time()), 'dependencies': [],
                'subject': {
                    'type': 'STATUS',
                    'value': {
                        'old': document['status'],
                        'new': new_status
                    }
                }
            }

            lock_token = DocumentService.get_document_lock(document['id'])
            DocumentService.update_document_by_log(document['id'], change_log, lock_token,
                                                   document['stateKey'] if 'stateKey' in document else None)
            DocumentService.release_document_lock(lock_token, document['id'])


def update_collaborations_status(document_package_id, requester_email, collaborator_email, status):

    import module.service.documentService as DocumentService
    documents = DocumentService.get_documents(document_package_id=document_package_id)

    for document in documents:
        DocumentService.update_collaboration_status(document['id'], requester_email, collaborator_email, status)


def get_document_package_status_statistics(document_package_id, include_collaborations=False,
                                           collaborators_to_filter=None):

    result = list(db.documents.aggregate([
        {'$match': {
            'documentPackageId': ObjectId(document_package_id)
        }},
        {'$project': {
            'checked': {
                '$cond': {
                    'if': {'$eq': ['$status', 'CHECKED']},
                    'then': 1, 'else': 0
                }
            },
            'prechecked': {
                '$cond': {
                    'if': {'$eq': ['$status', 'PRECHECKED']},
                    'then': 1, 'else': 0
                }
            },
            'unchecked': {
                '$cond': {
                    'if': {'$eq': ['$status', 'UNCHECKED']},
                    'then': 1, 'else': 0
                }
            }
        }},
        {'$group': {
            '_id': '$documentPackageId',
            'checked': {'$sum': '$checked'},
            'prechecked': {'$sum': '$prechecked'},
            'unchecked': {'$sum': '$unchecked'}
        }},
        {'$project': {
            '_id': 0,
            'checked': 1,
            'prechecked': 1,
            'unchecked': 1
        }}
    ]))

    if len(result) > 0:
        result = result[0]
    else:
        result = {'checked': 0, 'prechecked': 0, 'unchecked': 0}

    if include_collaborations:

        collaborators_match = {}
        if collaborators_to_filter and len(collaborators_to_filter) > 0:
            collaborators_match = {
                'collaborations.collaborator': {'$in': collaborators_to_filter}
            }

        collaborators_return = list(db.documents.aggregate([
            {'$match': {
                'documentPackageId': ObjectId(document_package_id)
            }},
            {'$unwind': "$collaborations"},
            {'$match': collaborators_match},
            {'$project': {
                '_id': 0,
                'collaborator': '$collaborations.collaborator',
                'uncheckedDone': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {'$eq': ['$status', 'UNCHECKED']},
                                {'$eq': ['$collaborations.status', 'DONE']}
                            ]
                        },
                        'then': 1, 'else': 0
                    }
                },
                'checkedDone': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {'$eq': ['$status', 'CHECKED']},
                                {'$eq': ['$collaborations.status', 'DONE']}
                            ]
                        },
                        'then': 1, 'else': 0
                    }
                },
                'precheckedDone': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {'$eq': ['$status', 'PRECHECKED']},
                                {'$eq': ['$collaborations.status', 'DONE']}
                            ]
                        },
                        'then': 1, 'else': 0
                    }
                },
                'uncheckedUndone': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {'$eq': ['$status', 'UNCHECKED']},
                                {'$eq': ['$collaborations.status', 'UNDONE']}
                            ]
                        },
                        'then': 1, 'else': 0
                    }
                },
                'checkedUndone': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {'$eq': ['$status', 'CHECKED']},
                                {'$eq': ['$collaborations.status', 'UNDONE']}
                            ]
                        },
                        'then': 1, 'else': 0
                    }
                },
                'precheckedUndone': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {'$eq': ['$status', 'PRECHECKED']},
                                {'$eq': ['$collaborations.status', 'UNDONE']}
                            ]
                        },
                        'then': 1, 'else': 0
                    }
                },
                'undone': {
                    '$cond': {
                        'if': {'$eq': ['$collaborations.status', 'UNDONE']},
                        'then': 1, 'else': 0
                    }
                },
                'done': {
                    '$cond': {
                        'if': {'$eq': ['$collaborations.status', 'DONE']},
                        'then': 1, 'else': 0
                    }
                },
                'reannotationDone': {
                    '$cond': {
                        'if': {'$eq': ['$collaborations.reannotation.status', 'DONE']},
                        'then': 1, 'else': 0
                    }
                },
                'warmUpDone': {
                    '$cond': {
                        'if': {'$eq': ['$collaborations.warmUp.status', 'DONE']},
                        'then': 1, 'else': 0
                    }
                }
            }},
            {'$group': {
                '_id': {
                    'collaborator': '$collaborator'
                },
                'checkedDone': {'$sum': '$checkedDone'},
                'precheckedDone': {'$sum': '$precheckedDone'},
                'uncheckedDone': {'$sum': '$uncheckedDone'},
                'checkedUndone': {'$sum': '$checkedUndone'},
                'precheckedUndone': {'$sum': '$precheckedUndone'},
                'uncheckedUndone': {'$sum': '$uncheckedUndone'},
                'undone': {'$sum': '$undone'},
                'done': {'$sum': '$done'},
                'reannotationDone': {'$sum': '$reannotationDone'},
                'warmUpDone': {'$sum': '$warmUpDone'}
            }},
            {'$project': {
                '_id': 0,
                'collaborator': '$_id.collaborator',
                'checkedDone': 1,
                'precheckedDone': 1,
                'uncheckedDone': 1,
                'checkedUndone': 1,
                'precheckedUndone': 1,
                'undone': 1,
                'done': 1,
                'uncheckedUndone': 1,
                'reannotationDone': 1,
                'warmUpDone': 1
            }}
        ]))

        result['collaborations'] = collaborators_return

    return result


def get_document_package_words_statistics(document_package_id=None, include_collaborations=False,
                                          collaborators_to_filter=None, document_package_ids=None):

    import module.service.documentService as DocumentService

    if document_package_ids:
        documents = DocumentService.get_documents(document_package_ids=document_package_ids)
    else:
        documents = DocumentService.get_documents(document_package_id=document_package_id)

    def get_subsentence(doc, subsentence_range):

        subsentence_range = [int(x) for x in subsentence_range.split(':')]

        form = []
        lemma = []

        for i in range(subsentence_range[1],subsentence_range[2]+1):
            form.append(doc['sentences'][subsentence_range[0]]['tokens'][i]['FORM'])
            lemma.append(doc['sentences'][subsentence_range[0]]['tokens'][i]['LEMMA'])

        return {
            'FORM': ' '.join(form),
            'LEMMA': ' '.join(lemma)
        }

    def fill_statistics(subsentence, statistics_to_fill):
        if subsentence not in statistics_to_fill:
            statistics_to_fill[subsentence] = 1
        else:
            statistics_to_fill[subsentence] += 1

    def get_token_statistics(doc):

        token_statistics = {
            'tags': {},
            'relations': {}
        }

        for tag in doc['tags']:

            if tag['label'] not in token_statistics['tags']:
                token_statistics['tags'][tag['label']] = {
                    'value': {'form': {}, 'lemma': {}},
                    'from-connector': {'form': {}, 'lemma': {}},
                    'to-connector': {'form': {}, 'lemma': {}}
                }

            subsentence = get_subsentence(doc, tag['range'])

            fill_statistics(subsentence['FORM'], token_statistics['tags'][tag['label']]['value']['form'])
            fill_statistics(subsentence['LEMMA'], token_statistics['tags'][tag['label']]['value']['lemma'])

        for relation in doc['relations']:

            if relation['label'] not in token_statistics['relations']:
                token_statistics['relations'][relation['label']] = {
                    'connector': {'form': {}, 'lemma': {}},
                    'from-tag': {'form': {}, 'lemma': {}},
                    'to-tag': {'form': {}, 'lemma': {}}
                }

            from_subsentence = get_subsentence(doc, relation['from']['range'])

            fill_statistics(from_subsentence['FORM'], token_statistics['relations'][relation['label']]['from-tag']['form'])
            fill_statistics(from_subsentence['LEMMA'], token_statistics['relations'][relation['label']]['from-tag']['lemma'])

            to_subsentence = get_subsentence(doc, relation['from']['range'])

            fill_statistics(to_subsentence['FORM'], token_statistics['relations'][relation['label']]['to-tag']['form'])
            fill_statistics(to_subsentence['LEMMA'], token_statistics['relations'][relation['label']]['to-tag']['lemma'])

            for connector in relation['connectors']:

                subsentence = get_subsentence(doc, connector)

                fill_statistics(subsentence['FORM'], token_statistics['relations'][relation['label']]['connector']['form'])
                fill_statistics(subsentence['LEMMA'], token_statistics['relations'][relation['label']]['connector']['lemma'])

                fill_statistics(subsentence['FORM'], token_statistics['tags'][relation['from']['label']]['from-connector']['form'])
                fill_statistics(subsentence['LEMMA'], token_statistics['tags'][relation['from']['label']]['from-connector']['lemma'])

                fill_statistics(subsentence['FORM'], token_statistics['tags'][relation['to']['label']]['to-connector']['form'])
                fill_statistics(subsentence['LEMMA'], token_statistics['tags'][relation['to']['label']]['to-connector']['lemma'])

        return token_statistics
    
    def get_merged_count_dict(dict1, dict2):

        merged = copy.deepcopy(dict1)
        for key in dict2:
            if key not in merged:
                merged[key] = dict2[key]
            else:
                merged[key] += dict2[key]

        return merged

    def get_merged_token_statistics(token_statistics1, token_statistics2):

        merged = copy.deepcopy(token_statistics1)

        for label in token_statistics2['tags']:

            if label not in merged['tags']:
                merged['tags'][label] = {
                    'value': {'form': {}, 'lemma': {}},
                    'from-connector': {'form': {}, 'lemma': {}},
                    'to-connector': {'form': {}, 'lemma': {}}
                }
                
            for stat_type in merged['tags'][label]:
                merged['tags'][label][stat_type]['form'] = get_merged_count_dict(
                    merged['tags'][label][stat_type]['form'], token_statistics2['tags'][label][stat_type]['form'])
                merged['tags'][label][stat_type]['lemma'] = get_merged_count_dict(
                    merged['tags'][label][stat_type]['lemma'], token_statistics2['tags'][label][stat_type]['lemma'])

        for label in token_statistics2['relations']:

            if label not in merged['relations']:
                merged['relations'][label] = {
                    'connector': {'form': {}, 'lemma': {}},
                    'from-tag': {'form': {}, 'lemma': {}},
                    'to-tag': {'form': {}, 'lemma': {}}
                }

            for stat_type in merged['relations'][label]:
                merged['relations'][label][stat_type]['form'] = get_merged_count_dict(
                    merged['relations'][label][stat_type]['form'], token_statistics2['relations'][label][stat_type]['form'])
                merged['relations'][label][stat_type]['lemma'] = get_merged_count_dict(
                    merged['relations'][label][stat_type]['lemma'], token_statistics2['relations'][label][stat_type]['lemma'])
                

        return merged

    result = {
        'documents': {},
        'collaborations': {}
    }

    for document in documents:

        token_statistics = get_token_statistics(document)

        result['documents'][document['id']] = token_statistics

        if 'all' not in result:
            result['all'] = token_statistics
        else:
            result['all'] = get_merged_token_statistics(result['all'], token_statistics)

        if include_collaborations:

            for collaboration in document['collaborations']:

                if not collaborators_to_filter or len(collaborators_to_filter) == 0 \
                        or collaboration['collaborator'] in collaborators_to_filter:

                    if collaboration['collaborator'] not in result['collaborations']:
                        result['collaborations'][collaboration['collaborator']] = {
                            'documents': {}
                        }

                    collaboration['sentences'] = document['sentences']
                    token_statistics = get_token_statistics(collaboration)

                    collaboration_result = result['collaborations'][collaboration['collaborator']]

                    collaboration_result['documents'][document['id']] = token_statistics

                    if 'all' not in collaboration_result:
                        collaboration_result['all'] = token_statistics
                    else:
                        collaboration_result['all'] = get_merged_token_statistics(collaboration_result['all'], token_statistics)

    return result


def get_document_package_tag_statistics(document_package_id, include_collaborations=False,
                                        collaborators_to_filter=None):

    import module.service.documentService as DocumentService
    documents = DocumentService.get_documents(document_package_id=document_package_id)

    count_by_tag = {}
    count_by_tag_by_collaborator = {}
    tags_frequency = {}

    for document in documents:
        if len(document['tags']) not in tags_frequency:
            tags_frequency[len(document['tags'])] = 1
        else:
            tags_frequency[len(document['tags'])] += 1

        for tag in document['tags']:
            if tag['label'] not in count_by_tag:
                count_by_tag[tag['label']] = 0
            count_by_tag[tag['label']] += 1

        if include_collaborations:
            for collaboration in document['collaborations']:

                if collaborators_to_filter and len(collaborators_to_filter) > 0 and \
                        collaboration['collaborator'] not in collaborators_to_filter:
                    continue

                if collaboration['collaborator'] not in count_by_tag_by_collaborator:
                    count_by_tag_by_collaborator[collaboration['collaborator']] = {}

                for tag in collaboration['tags']:
                    if tag['label'] not in count_by_tag_by_collaborator[collaboration['collaborator']]:
                        count_by_tag_by_collaborator[collaboration['collaborator']][tag['label']] = 0
                    count_by_tag_by_collaborator[collaboration['collaborator']][tag['label']] += 1

    result = {'values': [], 'collaborations': [], 'frequency': tags_frequency}

    for label in count_by_tag:
        result['values'].append({
            'label': label,
            'count': count_by_tag[label]
        })

    for collaborator in count_by_tag_by_collaborator:

        for label in count_by_tag_by_collaborator[collaborator]:

            result['collaborations'].append({
                'collaborator': collaborator,
                'label': label,
                'count': count_by_tag_by_collaborator[collaborator][label]
            })

    return result

    '''
    result['values'] = list(db.documents.aggregate([
        {'$match': {
            'documentPackageId': ObjectId(document_package_id)
        }},
        {'$unwind': '$tags'},
        {'$group': {
            '_id': {
                'tag': '$tags.label'
            },
            'count': {'$sum': 1},
        }},
        {'$project': {
            '_id': 0,
            'label': '$_id.tag',
            'count': 1
        }}
    ]))

    if include_collaborations:

        collaborators_match = {}
        if collaborators_to_filter and len(collaborators_to_filter) > 0:
            collaborators_match = {
                'collaborations.collaborator': {'$in': collaborators_to_filter}
            }

        collaborators_return = list(db.documents.aggregate([
            {'$match': {
                'documentPackageId': ObjectId(document_package_id)
            }},
            {'$unwind': "$collaborations"},
            {'$match': collaborators_match},
            {'$unwind': "$collaborations.tags"},
            {'$group': {
                '_id': {
                    'collaborator': '$collaborations.collaborator',
                    'tag': '$collaborations.tags.label'
                },
                'count': {'$sum': 1},
            }},
            {'$project': {
                '_id': 0,
                'collaborator': '$_id.collaborator',
                'label': '$_id.tag',
                'count': 1
            }}
        ]))

        result['collaborations'] = collaborators_return

    return result
    '''


def get_document_package_relation_statistics(document_package_id, include_collaborations=False,
                                             collaborators_to_filter=None):

    import module.service.documentService as DocumentService
    documents = DocumentService.get_documents(document_package_id=document_package_id)

    count_by_relation = {}
    count_by_relation_by_collaborator = {}
    relations_frequency = {}

    for document in documents:
        if len(document['relations']) not in relations_frequency:
            relations_frequency[len(document['relations'])] = 1
        else:
            relations_frequency[len(document['relations'])] += 1

        for relation in document['relations']:
            if relation['label'] not in count_by_relation:
                count_by_relation[relation['label']] = 0
            count_by_relation[relation['label']] += 1

        if include_collaborations:
            for collaboration in document['collaborations']:

                if collaborators_to_filter and len(collaborators_to_filter) > 0 and \
                                collaboration['collaborator'] not in collaborators_to_filter:
                    continue

                if collaboration['collaborator'] not in count_by_relation_by_collaborator:
                    count_by_relation_by_collaborator[collaboration['collaborator']] = {}

                for relation in collaboration['relations']:
                    if relation['label'] not in count_by_relation_by_collaborator[collaboration['collaborator']]:
                        count_by_relation_by_collaborator[collaboration['collaborator']][relation['label']] = 0
                    count_by_relation_by_collaborator[collaboration['collaborator']][relation['label']] += 1

    result = {'values': [], 'collaborations': [], 'frequency': relations_frequency}

    for label in count_by_relation:
        result['values'].append({
            'label': label,
            'count': count_by_relation[label]
        })

    for collaborator in count_by_relation_by_collaborator:

        for label in count_by_relation_by_collaborator[collaborator]:

            result['collaborations'].append({
                'collaborator': collaborator,
                'label': label,
                'count': count_by_relation_by_collaborator[collaborator][label]
            })

    return result
    
    '''
    result = {}

    result['values'] = list(db.documents.aggregate([
        {'$match': {
            'documentPackageId': ObjectId(document_package_id)
        }},
        {'$unwind': '$relations'},
        {'$group': {
            '_id': {
                'relation': '$relations.label'
            },
            'count': {'$sum': 1},
        }},
        {'$project': {
            '_id': 0,
            'label': '$_id.relation',
            'count': 1
        }}
    ]))

    if include_collaborations:

        collaborators_match = {}
        if collaborators_to_filter and len(collaborators_to_filter) > 0:
            collaborators_match = {
                'collaborations.collaborator': {'$in': collaborators_to_filter}
            }

        collaborators_return = list(db.documents.aggregate([
            {'$match': {
                'documentPackageId': ObjectId(document_package_id)
            }},
            {'$unwind': "$collaborations"},
            {'$match': collaborators_match},
            {'$unwind': "$collaborations.relations"},
            {'$group': {
                '_id': {
                    'collaborator': '$collaborations.collaborator',
                    'relation': '$collaborations.relations.label'
                },
                'count': {'$sum': 1},
            }},
            {'$project': {
                '_id': 0,
                'collaborator': '$_id.collaborator',
                'label': '$_id.relation',
                'count': 1
            }}
        ]))

        result['collaborations'] = collaborators_return

    return result
    '''


def get_document_package_connector_statistics(document_package_id, include_collaborations=False,
                                              collaborators_to_filter=None):

    import module.service.documentService as DocumentService
    documents = DocumentService.get_documents(document_package_id=document_package_id)

    count_by_connector = {}
    count_by_connector_by_collaborator = {}
    connectors_frequency = {}

    for document in documents:

        connectors_count = 0

        for relation in document['relations']:

            connectors_count += len(relation['connectors'])

            if relation['label'] not in count_by_connector:
                count_by_connector[relation['label']] = 0
            count_by_connector[relation['label']] += len(relation['connectors'])

        if connectors_count not in connectors_frequency:
            connectors_frequency[connectors_count] = 1
        else:
            connectors_frequency[connectors_count] += 1

        if include_collaborations:
            for collaboration in document['collaborations']:

                for collaboration_relation in collaboration['relations']:

                    relation_label = collaboration_relation['label']

                    if collaborators_to_filter and len(collaborators_to_filter) > 0 and \
                                    collaboration['collaborator'] not in collaborators_to_filter:
                        continue

                    if collaboration['collaborator'] not in count_by_connector_by_collaborator:
                        count_by_connector_by_collaborator[collaboration['collaborator']] = {}

                    for connector in collaboration_relation['connectors']:
                        if relation_label not in count_by_connector_by_collaborator[collaboration['collaborator']]:
                            count_by_connector_by_collaborator[collaboration['collaborator']][relation_label] = 0
                        count_by_connector_by_collaborator[collaboration['collaborator']][relation_label] += 1

    result = {'values': [], 'collaborations': [], 'frequency': connectors_frequency}

    for label in count_by_connector:
        result['values'].append({
            'label': label,
            'count': count_by_connector[label]
        })

    for collaborator in count_by_connector_by_collaborator:

        for label in count_by_connector_by_collaborator[collaborator]:

            result['collaborations'].append({
                'collaborator': collaborator,
                'label': label,
                'count': count_by_connector_by_collaborator[collaborator][label]
            })

    return result
    
    '''
    result = {}

    result['values'] = list(db.documents.aggregate([
        {'$match': {
            'documentPackageId': ObjectId(document_package_id)
        }},
        {'$unwind': '$relations'},
        {'$unwind': '$relations.connectors'},
        {'$group': {
            '_id': {
                'relation': '$relations.label'
            },
            'count': {'$sum': 1},
        }},
        {'$project': {
            '_id': 0,
            'label': '$_id.relation',
            'count': 1
        }}
    ]))

    if include_collaborations:

        collaborators_match = {}
        if collaborators_to_filter and len(collaborators_to_filter) > 0:
            collaborators_match = {
                'collaborations.collaborator': {'$in': collaborators_to_filter}
            }

        collaborators_return = list(db.documents.aggregate([
            {'$match': {
                'documentPackageId': ObjectId(document_package_id)
            }},
            {'$unwind': "$collaborations"},
            {'$match': collaborators_match},
            {'$unwind': "$collaborations.relations"},
            {'$unwind': '$collaborations.relations.connectors'},
            {'$group': {
                '_id': {
                    'collaborator': '$collaborations.collaborator',
                    'relation': '$collaborations.relations.label'
                },
                'count': {'$sum': 1},
            }},
            {'$project': {
                '_id': 0,
                'collaborator': '$_id.collaborator',
                'label': '$_id.relation',
                'count': 1
            }}
        ]))

        result['collaborations'] = collaborators_return

    return result
    '''


def get_document_package_token_statistics(document_package_id, include_collaborations=False,
                                             collaborators_to_filter=None):

    import module.service.documentService as DocumentService
    documents = DocumentService.get_documents(document_package_id=document_package_id)

    result = {'values': {'tag': 0, 'empty': 0, 'connector': 0}, 'frequency': {}}
    if include_collaborations:
        result['collaborations'] = []

    def fill_result(doc, bucket):

        for tag in doc['tags']:
            tag_range = tag['range'].split(':')
            coverage = abs(int(tag_range[1]) - int(tag_range[2])) + 1
            bucket['tag'] += coverage
            bucket['empty'] -= coverage

        for relation in doc['relations']:
            for connector in relation['connectors']:
                connector_range = connector.split(':')
                coverage = abs(int(connector_range[1]) - int(connector_range[2])) + 1
                bucket['connector'] += coverage
                bucket['empty'] -= coverage

    collaboration_result_map = {}
    for document in documents:

        tokens_count = 0

        for sentence in document['sentences']:
            tokens_count += len(sentence['tokens'])

        if tokens_count not in result['frequency']:
            result['frequency'][tokens_count] = 1
        else:
            result['frequency'][tokens_count] += 1

        tokens_count = 0
        for sentence in document['sentences']:
            tokens_count += len(sentence['tokens'])
        result['values']['empty'] += tokens_count

        fill_result(document, result['values'])

        for collaboration in document['collaborations']:
            if not collaborators_to_filter or collaboration['collaborator'] in collaborators_to_filter:

                if collaboration['collaborator'] not in collaboration_result_map:
                    collaboration_result = {'collaborator': collaboration['collaborator'],
                                            'tag': 0, 'empty': tokens_count, 'connector': 0}
                    collaboration_result_map[collaboration['collaborator']] = collaboration_result
                    result['collaborations'].append(collaboration_result)
                else:
                    collaboration_result_map[collaboration['collaborator']]['empty'] += tokens_count

                fill_result(collaboration, collaboration_result_map[collaboration['collaborator']])

    return result


def get_document_package_summary_statistics(document_package_id, include_collaborations=False,
                                            collaborators_to_filter=None):

    import module.service.documentService as DocumentService
    documents = DocumentService.get_documents(document_package_id=document_package_id)

    result = []

    def get_summary(doc):

        time_spent = 0
        number_of_views = 0
        doneAt = None
        previous_action = None

        for action in doc['logs']:
            if action['action'] == 'CHANGE' and action['subject']['type'] == 'STATUS' and \
                            action['subject']['value']['new'] == 'DONE':
                doneAt = action['atTime']

            if action['action'] == 'OPEN':
                previous_action = action
                number_of_views += 1
                continue
            elif action['action'] == 'CHANGE' and action['subject']['type'] == 'STATUS' and \
                            action['subject']['value']['new'] == 'UNDONE':
                previous_action = None
                continue
            elif previous_action:
                time_spent += action['atTime'] - previous_action['atTime']
            previous_action = action

        return {'timeSpent': time_spent, 'numberOfViews': number_of_views, 'doneAt': doneAt}

    for document in documents:

        summary = get_summary(document)

        if include_collaborations:

            summary['collaborationsSummary'] = {}
            summary['collaborations'] = {}
            time_spent_list = []
            number_of_views_list = []

            for collaboration in document['collaborations']:

                if not collaborators_to_filter or collaboration['collaborator'] in collaborators_to_filter:

                    collaboration_summary = get_summary(collaboration)

                    time_spent_list.append(collaboration_summary['timeSpent'])
                    number_of_views_list.append(collaboration_summary['numberOfViews'])

                    summary['collaborations'][collaboration['collaborator']] = collaboration_summary

                    # summary['collaborations'].append(collaboration_summary)

            summary['collaborationsSummary']['timeSpentSum'] = sum(time_spent_list)
            summary['collaborationsSummary']['timeSpentMean'] = statistics.mean(time_spent_list)
            summary['collaborationsSummary']['timeSpentStandardDeviation'] = statistics.pstdev(time_spent_list)
            summary['collaborationsSummary']['numberOfViewsSum'] = sum(number_of_views_list)
            summary['collaborationsSummary']['numberOfViewsMean'] = statistics.mean(number_of_views_list)
            summary['collaborationsSummary']['numberOfViewsStandardDeviation'] = statistics.pstdev(number_of_views_list)

        summary['id'] = document['id']
        summary['name'] = document['name']

        tokens_count = 0
        for sentence in document['sentences']:
            tokens_count += len(sentence['tokens'])

        summary['numberOfTokens'] = tokens_count

        result.append(summary)

    return result


def get_document_map(document, map_types=['tag', 'relation', 'connector'], tag_prefix ='TAG',
                     relation_prefix ='RELATION', connector_prefix = 'CONNECTOR', start_prefix = 'B-',
                     inner_prefix = 'I-', empty_flag ='O'):

    result = {}

    if 'tag' in map_types:

        # filling token by token with correspondent tag
        for tag in document['tags']:
            tag_range = tag['range'].split(':')
            s_index = int(tag_range[0])
            for t_index in range(int(tag_range[1]), int(tag_range[2])+1):

                # 01.txt:0:0 = T:Y
                # <DOCUMENT_ID>:<SENTENCE_ID>:<TOKEN_ID> = <TAG_PREFIX> : <TAG_LABEL>
                key = document['id'] + ':' + str(s_index) + ':' + str(t_index)
                '''
                if t_index == int(tag_range[1]):
                    result[key] = start_prefix + tag['label']
                else:
                    result[key] = inner_prefix + tag['label']
                '''
                result[key] = tag_prefix + ':' + tag['label']

        # filling empty spaces
        for s_index in range(0, len(document['sentences'])):
            for t_index in range(0, len(document['sentences'][s_index]['tokens'])):
                key = document['id'] + ':' + str(s_index) + ':' + str(t_index)
                if key not in result:
                    result[key] = tag_prefix + ':' + empty_flag

    if 'relation' in map_types or 'connector' in map_types:

        #  document_relation_keys = {}

        # handling relations
        for relation in document['relations']:

            # splitting tags and creating fake relations (making all tokens combinations)
            from_tag_range = relation['from']['range'].split(':')
            from_tag_label = relation['from']['label']
            from_sentence_index = int(from_tag_range[0])
            to_tag_range = relation['to']['range'].split(':')
            to_tag_label = relation['to']['label']
            to_sentence_index = int(to_tag_range[0])

            for from_t_index in range(int(from_tag_range[1]), int(from_tag_range[2]) + 1):
                for to_t_index in range(int(to_tag_range[1]), int(to_tag_range[2]) + 1):

                    if 'relation' in map_types:

                        # 01.txt:0:0:Y:0:4:Z = R:hasZ
                        # <DOCUMENT_ID>:<FROM_SENTENCE_ID>:<FROM_TOKEN_ID>:<FROM_LABEL>:<TO_SENTENCE_ID>:<TO_TOKEN_ID>:<TO_LABEL> = <TYPE_PREFIX>:<RELATION_LABEL>

                        key = document['id'] + \
                              ':' + str(from_sentence_index) + ':' + str(from_t_index) + ':' + from_tag_label + \
                              ':' + str(to_sentence_index) + ':' + str(to_t_index) + ':' + to_tag_label
                        '''
                        key = document['id'] + ':' + relation_prefix + ':' + relation['label'] + \
                              ':' + str(from_sentence_index) + ':' + str(from_t_index) + ':' + from_tag_label + \
                              ':' + str(to_sentence_index) + ':' + str(to_t_index) + ':' + to_tag_label
                        '''

                        result[key] = relation_prefix + ':' + relation['label']
                        #  document_relation_keys[key] = relation['label']

                    if 'connector' in map_types:

                        # handling connectors
                        for connector in relation['connectors']:
                            connector_range = connector.split(':')
                            connector_sentence_index = int(connector_range[0])
                            for connector_t_index in range(int(connector_range[1]), int(connector_range[2]) + 1):

                                # 01.txt:0:0:Y:0:4:Z:0:2 = C:hasZ
                                # <DOCUMENT_ID>:<FROM_SENTENCE_ID>:<FROM_TOKEN_ID>:<FROM_LABEL>:<TO_SENTENCE_ID>:<TO_TOKEN_ID>:<TO_LABEL>:<CONNECTOR_SENTENCE_ID>:<CONNECTOR_TOKEN_ID> = <TYPE_PREFIX>:<RELATION_LABEL>

                                key = document['id'] + \
                                      ':' + str(from_sentence_index) + ':' + str(from_t_index) + ':' + from_tag_label + \
                                      ':' + str(to_sentence_index) + ':' + str(to_t_index) + ':' + to_tag_label + \
                                      ':' + str(connector_sentence_index) + ':' + str(connector_t_index)
                                '''
                                key = document['id'] + ':' + connector_prefix + ':' + str(connector_t_index) + \
                                      ':' + relation['label'] + str(from_sentence_index) + ':' + str(from_t_index) + \
                                      ':' + from_tag_label + ':' + str(to_sentence_index) + ':' + str(to_t_index) + \
                                      ':' + to_tag_label
                                '''

                                result[key] = connector_prefix + ':' + relation['label']
                                #  document_relation_keys[key] = relation['label']

    return result


def get_document_package_agreement_statistics(document_package_id, document_id=None,
                                              agreement_types=['tag', 'relation', 'connector'],
                                              collaborators_to_filter=None):

    EMPTY_FLAG = 'O'

    import module.service.documentService as DocumentService

    if not document_id:
        documents = DocumentService.get_documents(document_package_id=document_package_id)
    else:
        documents = [DocumentService.get_document(document_id, False, False, False)]

    document_package = get_document_package(document_package_id)
    group_by_collaborator = {}

    for collaborator in document_package['collaborators']:
        group_by_collaborator[collaborator['email']] = collaborator['group']

    def get_cohen_kappa_agreement(map1, map2):

        new_map1 = {}
        new_map2 = {}

        all_keys = set(list(map2.keys()) + list(map1.keys()))

        for k in all_keys:

            if k not in map1:
                value_prefix = map2[k].split(':')[0]
                new_map1[k] = value_prefix + ':' + EMPTY_FLAG
            else:
                new_map1[k] = map1[k]

            if k not in map2:
                value_prefix = map1[k].split(':')[0]
                new_map2[k] = value_prefix + ':' + EMPTY_FLAG
            else:
                new_map2[k] = map2[k]

        cohen_kappa_matrix = Statistics.build_cohen_kappa_matrix(new_map1, new_map2)
        return Statistics.cohen_kappa(cohen_kappa_matrix)

    document_map_cache = {}

    def get_document_map_from_cache(doc, key_prefix='D'):

        cache_key = key_prefix + '-' + doc['id']

        if 'collaborator' in doc:
            cache_key += ':' + doc['collaborator']

        if cache_key in document_map_cache:
            return document_map_cache[cache_key]

        return get_document_map(doc, map_types=agreement_types, empty_flag=EMPTY_FLAG)

    result = {
        'all': {
            'agreement': {}
        }
    }

    document_maps_by_collaborator = {}

    for document in documents:

        result[document['id']] = {'agreement': {}}

        gsa_map = None
        if document['status'] == 'CHECKED':
            gsa_map = get_document_map_from_cache(document)

            if '(GSA)' not in document_maps_by_collaborator:
                document_maps_by_collaborator['(GSA)'] = {}
            document_maps_by_collaborator['(GSA)'][document['id']] = gsa_map

        for collaboration in document['collaborations']:

            if collaboration['status'] != 'DONE' or \
                (collaborators_to_filter and len(collaborators_to_filter) > 0 \
                 and collaboration['collaborator'] not in collaborators_to_filter):
                continue

            collaboration['id'] = document['id']
            collaboration['sentences'] = document['sentences']
            collaboration_map = get_document_map_from_cache(collaboration)

            if collaboration['collaborator'] not in document_maps_by_collaborator:
                document_maps_by_collaborator[collaboration['collaborator']] = {}
            document_maps_by_collaborator[collaboration['collaborator']][document['id']] = collaboration_map

            if gsa_map:  # GSA agreement
                agreement_key = '(GSA):' + collaboration['collaborator']
                result[document['id']]['agreement'][agreement_key] = {
                    'cohenKappa' : get_cohen_kappa_agreement(gsa_map, collaboration_map)
                }

            if collaboration['collaborator'] in group_by_collaborator:  # self-agreement

                collaborator_group = group_by_collaborator[collaboration['collaborator']]

                if collaborator_group and collaborator_group['reannotationStep'] > 0 and \
                        'reannotation' in collaboration and collaboration['reannotation']['status'] == 'DONE':

                    collaboration['reannotation']['id'] = document['id']
                    collaboration['reannotation']['sentences'] = document['sentences']
                    reannotation_map = get_document_map_from_cache(collaboration['reannotation'], 'R')

                    agreement_key = collaboration['collaborator'] + ':' + collaboration['collaborator']
                    result[document['id']]['agreement'][agreement_key] = {
                        'cohenKappa' : get_cohen_kappa_agreement(reannotation_map, collaboration_map)
                    }
                    document_maps_by_collaborator[collaboration['collaborator']]['R-' + document['id']] = reannotation_map

            for other_collaboration in document['collaborations']:  # commom agreement

                if other_collaboration['status'] != 'DONE' or \
                    (collaborators_to_filter and len(collaborators_to_filter) > 0 and \
                     other_collaboration['collaborator'] not in collaborators_to_filter) or \
                     collaboration['collaborator'] == other_collaboration['collaborator']:
                    continue

                other_collaboration['id'] = document['id']
                other_collaboration['sentences'] = document['sentences']

                agreement_key = collaboration['collaborator'] + ':' + other_collaboration['collaborator']
                inverse_agreement_key = other_collaboration['collaborator'] + ':' + collaboration['collaborator']

                if agreement_key in result[document['id']] or inverse_agreement_key in result[document['id']]:
                    continue

                other_collaboration_map = get_document_map_from_cache(other_collaboration)

                result[document['id']]['agreement'][agreement_key] = {
                    'cohenKappa' : get_cohen_kappa_agreement(other_collaboration_map, collaboration_map)
                }

                if other_collaboration['collaborator'] not in document_maps_by_collaborator:
                    document_maps_by_collaborator[other_collaboration['collaborator']] = {}
                document_maps_by_collaborator[other_collaboration['collaborator']][document['id']] = other_collaboration_map

        if not result[document['id']]:
            del result[document['id']]

    # all documents agreement:

    for collaborator in document_maps_by_collaborator:

        all_maps = []
        all_reannotation_maps = []
        all_base_reannotation_maps = []
        valid_document_ids = []

        for document_id in document_maps_by_collaborator[collaborator]:
            if document_id.startswith('R-'):
                all_base_reannotation_maps.append(document_maps_by_collaborator[collaborator][document_id.replace('R-', '')])
                all_reannotation_maps.append(document_maps_by_collaborator[collaborator][document_id])
            else:
                valid_document_ids.append(document_id)
                all_maps.append(document_maps_by_collaborator[collaborator][document_id])

        if len(all_reannotation_maps) > 0:
            # self-agreement
            agreement_key = collaborator + ':' + collaborator
            result['all']['agreement'][agreement_key] = {
                'cohenKappa' : get_cohen_kappa_agreement(ObjectUtil.merge_dicts(*all_base_reannotation_maps),
                                                         ObjectUtil.merge_dicts(*all_reannotation_maps))
            }

        for other_collaborator in document_maps_by_collaborator:

            if collaborator == other_collaborator:
                continue

            agreement_key = collaborator + ':' + other_collaborator
            inverse_agreement_key = other_collaborator + ':' + collaborator

            all_other_maps = []

            if agreement_key not in result['all']['agreement'] and inverse_agreement_key not in result['all']['agreement']:
                for document_id in document_maps_by_collaborator[other_collaborator]:
                    if not document_id.startswith('R-') and document_id in valid_document_ids:
                        all_other_maps.append(document_maps_by_collaborator[other_collaborator][document_id])

                # agreement
                result['all']['agreement'][agreement_key] = {
                    'cohenKappa' : get_cohen_kappa_agreement(ObjectUtil.merge_dicts(*all_maps),
                                                             ObjectUtil.merge_dicts(*all_other_maps))
                }

    return result


'''
def get_document_package_agreement_statistics(document_package_id, document_id=None,
                                              agreement_types=['tag', 'relation', 'connector'],
                                              collaborators_to_filter=None, only_done_collaborations=True,
                                              only_checked_documents=True):

    REANNOTATION_MAP_PREFIX = 'R'
    EMPTY_FLAG = 'O'

    import module.service.documentService as DocumentService

    if not document_id:
        documents = DocumentService.get_documents(document_package_id=document_package_id)
    else:
        documents = [DocumentService.get_document(document_id, False, False, False)]

    document_package = get_document_package(document_package_id)
    group_by_collaborator = {}

    for collaborator in document_package['collaborators']:
        group_by_collaborator[collaborator['email']] = collaborator['group']

    agreements = {
        'all': {
            'agreement': {},
            # 'map': {},
            'collaborationsMaps': {}
        }
    }

    valid_collaborators = set()

    # building maps

    for document in documents:

        agreements[document['id']] = {
            'agreement': {},
            # 'map': {},
            'collaborationsMaps': {}
        }

        if not only_checked_documents or (only_checked_documents and document['status'] == 'CHECKED'):
            document['collaborator'] = '(GSA)'
            document['status'] = 'DONE'
            document['collaborations'].append(document)

            # agreements[document['id']]['map'] = get_document_map(document, map_types=agreement_types, empty_flag=EMPTY_FLAG)
            # agreements['all']['map'] = ObjectUtil.merge_dicts(agreements['all']['map'], agreements[document['id']]['map'])

        for collaboration in document['collaborations']:

            if only_done_collaborations and collaboration['status'] != 'DONE':
                continue

            if not collaborators_to_filter or collaboration['collaborator'] == '(GSA)' or collaboration['collaborator'] in collaborators_to_filter:

                valid_collaborators.add(collaboration['collaborator'])

                collaboration['id'] = document['id']
                collaboration['sentences'] = document['sentences']

                collaboration_map = get_document_map(collaboration, map_types=agreement_types, empty_flag=EMPTY_FLAG)

                agreements[document['id']]['collaborationsMaps'][collaboration['collaborator']] = collaboration_map

                if collaboration['collaborator'] not in agreements['all']['collaborationsMaps']:
                    agreements['all']['collaborationsMaps'][collaboration['collaborator']] = collaboration_map
                else:
                    agreements['all']['collaborationsMaps'][collaboration['collaborator']] = ObjectUtil.merge_dicts(
                        agreements['all']['collaborationsMaps'][collaboration['collaborator']], collaboration_map)

            if collaboration['collaborator'] in group_by_collaborator:

                collaborator_group = group_by_collaborator[collaboration['collaborator']]

                if collaborator_group and collaborator_group['reannotationStep'] > 0 and \
                   'reannotation' in collaboration and len(collaboration['reannotation']['logs']) > 0:

                    # has reannotation

                    if only_done_collaborations and collaboration['reannotation']['status'] != 'DONE':
                        continue

                    collaboration['reannotation']['id'] = document['id']
                    collaboration['reannotation']['sentences'] = document['sentences']

                    reannotation_map = get_document_map(collaboration['reannotation'], map_types=agreement_types,
                                                        empty_flag=EMPTY_FLAG)
                    reannotation_key = REANNOTATION_MAP_PREFIX + ':' + collaboration['collaborator']

                    agreements[document['id']]['collaborationsMaps'][reannotation_key] = reannotation_map

                    if reannotation_key not in agreements['all']['collaborationsMaps']:
                        agreements['all']['collaborationsMaps'][reannotation_key] = reannotation_map
                    else:
                        agreements['all']['collaborationsMaps'][reannotation_key] = ObjectUtil.merge_dicts(
                            agreements['all']['collaborationsMaps'][reannotation_key], reannotation_map)

    if 'relation' in agreement_types or 'connector' in agreement_types:

        # fixing collaborator lack of some relations/connectors

        all_keys = set()
        all_keys_by_document = {}

        for collaboration_key, collaboration_map in agreements['all']['collaborationsMaps'].items():
            for key, value in collaboration_map.items():
                all_keys.add(key)

        for document in documents:
            if document['id'] not in agreements:
                continue
            all_keys_by_document[document['id']] = set()
            for collaboration_key, collaboration_map in agreements[document['id']]['collaborationsMaps'].items():
                for key, value in collaboration_map.items():
                    all_keys_by_document[document['id']].add(key)

        def fix_map(map_to_fix, valid_keys):
            for key in valid_keys:
                if key not in map_to_fix:
                    map_to_fix[key] = EMPTY_FLAG

        #fix_map(agreements['all']['map'], all_keys)
        for collaboration_key, collaboration_map in agreements['all']['collaborationsMaps'].items():
            fix_map(collaboration_map, all_keys)

        for document in documents:
            if document['id'] not in agreements:
                continue
            #fix_map(agreements[document['id']]['map'], all_keys_by_document[document['id']])
            for collaboration_key, collaboration_map in agreements[document['id']]['collaborationsMaps'].items():
                fix_map(collaboration_map, all_keys_by_document[document['id']])

    # filling agreements

    def get_cohen_kappa_agreement(map1, map2):
        cohen_kappa_matrix = Statistics.build_cohen_kappa_matrix(map1, map2)
        return Statistics.cohen_kappa(cohen_kappa_matrix)

    def fill_agreements(agreement_key):

        for collaborator_1 in valid_collaborators:

            if collaborator_1 in agreements[agreement_key]['collaborationsMaps']:

                collaborator_1_map = agreements[agreement_key]['collaborationsMaps'][collaborator_1]

                for collaborator_2 in valid_collaborators:

                    collaborator_agreement_key = collaborator_1 + ':' + collaborator_2
                    inverse_collaborator_agreement_key = collaborator_2 + ':' + collaborator_1

                    if collaborator_agreement_key not in agreements[agreement_key]['agreement'] and \
                                    inverse_collaborator_agreement_key not in agreements[agreement_key]['agreement']:

                        map_key = collaborator_2 if collaborator_1 != collaborator_2 \
                            else REANNOTATION_MAP_PREFIX + ':' + collaborator_2

                        if map_key in agreements[agreement_key]['collaborationsMaps']:

                            collaborator_2_map = agreements[agreement_key]['collaborationsMaps'][map_key]

                            agreements[agreement_key]['agreement'][collaborator_agreement_key] = {
                                'cohenKappa': get_cohen_kappa_agreement(collaborator_1_map, collaborator_2_map)
                            }

    fill_agreements('all')
    #del agreements['all']['map']
    del agreements['all']['collaborationsMaps']

    for document in documents:
        if document['id'] in agreements:
            fill_agreements(document['id'])
            #del agreements[document['id']]['map']
            del agreements[document['id']]['collaborationsMaps']

    return agreements
'''