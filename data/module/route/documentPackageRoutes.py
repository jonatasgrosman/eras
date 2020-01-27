import module.util.routeUtil as RouteUtil
import module.service.documentPackageService as DocumentPackageService
import module.service.documentService as DocumentService
from flask import request, g, make_response, send_file
from module import app
import base64
import tempfile
import zipfile


@app.route('/document-package', methods=['GET', 'POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_package_root():

    ids = request.args.get('ids')
    project_id = request.args.get('projectId')
    collaborator_email = request.args.get('collaboratorEmail')
    append_statistics = request.args.get('appendStatistics')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    if request.method == 'GET':

        if ids:
            return RouteUtil.data_to_json_response(
                DocumentPackageService.get_document_packages(ids.split(","), append_statistics=append_statistics))

        elif project_id:
            return RouteUtil.data_to_json_response(
                DocumentPackageService.get_document_packages_by_project(project_id,
                                                                        append_statistics=append_statistics))

        elif collaborator_email:
            return RouteUtil.data_to_json_response(
                DocumentPackageService.get_document_packages_by_collaborator(collaborator_email,
                                                                             append_statistics=append_statistics))

        else:
            return RouteUtil.data_to_json_response(
                DocumentPackageService.get_document_packages(skip=skip, limit=limit,
                                                             append_statistics=append_statistics))

    elif request.method == 'POST':

        return DocumentPackageService.create_document_package(RouteUtil.safe_json_get('projectId'),
                                                              RouteUtil.safe_json_get('name'),
                                                              RouteUtil.safe_json_get('randomAnnotation'),
                                                              RouteUtil.safe_json_get('showSelfAgreementFeedback'),
                                                              RouteUtil.safe_json_get('selfAgreementFeedbackGoal'),
                                                              RouteUtil.safe_json_get('usePrecheckAgreementThreshold'),
                                                              RouteUtil.safe_json_get('precheckAgreementThreshold'),
                                                              RouteUtil.safe_json_get('useTagAgreement'),
                                                              RouteUtil.safe_json_get('useRelationAgreement'),
                                                              RouteUtil.safe_json_get('useConnectorAgreement'))


@app.route('/document-package/<document_package_id>', methods=['GET', 'POST', 'DELETE'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_package(document_package_id):

    append_statistics = request.args.get('appendStatistics')

    if request.method == 'GET':
        return RouteUtil.data_to_json_response(
            DocumentPackageService.get_document_package(document_package_id, append_statistics=append_statistics), True)

    elif request.method == 'POST':
        DocumentPackageService.update_document_package(document_package_id,
                                                       RouteUtil.safe_json_get('name'),
                                                       RouteUtil.safe_json_get('randomAnnotation'),
                                                       RouteUtil.safe_json_get('showSelfAgreementFeedback'),
                                                       RouteUtil.safe_json_get('selfAgreementFeedbackGoal'),
                                                       RouteUtil.safe_json_get('usePrecheckAgreementThreshold'),
                                                       RouteUtil.safe_json_get('precheckAgreementThreshold'),
                                                       RouteUtil.safe_json_get('useTagAgreement'),
                                                       RouteUtil.safe_json_get('useRelationAgreement'),
                                                       RouteUtil.safe_json_get('useConnectorAgreement'))
        return 'OK', 200

    elif request.method == 'DELETE':
        DocumentPackageService.remove_document_package(document_package_id)
        return 'OK', 200


@app.route('/document-package/<document_package_id>/collaborator', methods=['GET', 'POST', 'DELETE'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_package_collaborator(document_package_id):

    email = request.args.get('email')

    if request.method == 'GET':

        if email:
            return RouteUtil.data_to_json_response(
                DocumentPackageService.get_document_packages_by_collaborator(document_package_id, email))
        else:
            return RouteUtil.data_to_json_response(
                DocumentPackageService.get_document_package_collaborators(document_package_id))

    elif request.method == 'POST':

        if email: # update
            DocumentPackageService.update_document_package_collaborator(document_package_id,
                                                                        RouteUtil.safe_json_get('groupId'), email)
        else:
            DocumentPackageService.insert_document_package_collaborator(document_package_id,
                                                                        RouteUtil.safe_json_get('groupId'),
                                                                        RouteUtil.safe_json_get('email'))

        return 'OK', 200

    elif request.method == 'DELETE':
        DocumentPackageService.remove_document_package_collaborator(document_package_id, email)
        return 'OK', 200


@app.route('/document-package/<document_package_id>/group', methods=['GET', 'POST', 'DELETE'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_package_group(document_package_id):

    group_id = request.args.get('groupId')
    collaborator_email = request.args.get('collaboratorEmail')

    if request.method == 'GET':

        if group_id or collaborator_email:
            if group_id:
                return RouteUtil.data_to_json_response(
                    DocumentPackageService.get_document_package_group(document_package_id, int(group_id)))
            else:
                return RouteUtil.data_to_json_response(
                    DocumentPackageService.get_document_package_group_by_collaborator_email(document_package_id, collaborator_email))
        else:
            return RouteUtil.data_to_json_response(
                DocumentPackageService.get_document_package_groups(document_package_id))

    elif request.method == 'POST':

        if group_id: # update
            DocumentPackageService.update_document_package_group(document_package_id, int(group_id),
                                                                 RouteUtil.safe_json_get('name'),
                                                                 RouteUtil.safe_json_get('warmUpSize'),
                                                                 RouteUtil.safe_json_get('reannotationStep'))
        else:
            return str(DocumentPackageService.insert_document_package_group(document_package_id,
                                                                            RouteUtil.safe_json_get('name'),
                                                                            RouteUtil.safe_json_get('warmUpSize'),
                                                                            RouteUtil.safe_json_get('reannotationStep'))
                       )

        return 'OK', 200

    elif request.method == 'DELETE':
        DocumentPackageService.remove_document_package_group(document_package_id, int(group_id))
        return 'OK', 200


@app.route('/document-package/<document_package_id>/statistics', methods=['GET'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_package_statistics(document_package_id):

    collaborator_email = request.args.get('collaboratorEmail')
    append_agreement = RouteUtil.value_to_boolean(request.args.get('appendAgreement'))

    if collaborator_email:
        return RouteUtil.data_to_json_response(
            DocumentPackageService.get_document_package_collaborator_statistics(document_package_id,
                                                                                collaborator_email,
                                                                                append_agreement))
    else:

        statistics_type = request.args.get('type')
        statistics_filter = request.args.get('filter')
        append_collaborations = request.args.get('appendCollaborations')
        collaborators_to_filter = request.args.get('collaboratorsToFilter')
        if collaborators_to_filter:
            collaborators_to_filter = collaborators_to_filter.split(',')

        if statistics_type == 'token':
            return RouteUtil.data_to_json_response(
                DocumentPackageService.
                    get_document_package_token_statistics(document_package_id=document_package_id,
                                                          include_collaborations=append_collaborations,
                                                          collaborators_to_filter=collaborators_to_filter))

        elif statistics_type == 'tag':
            return RouteUtil.data_to_json_response(
                DocumentPackageService.
                    get_document_package_tag_statistics(document_package_id=document_package_id,
                                                        include_collaborations=append_collaborations,
                                                        collaborators_to_filter=collaborators_to_filter))
        elif statistics_type == 'relation':
            return RouteUtil.data_to_json_response(
                DocumentPackageService.
                    get_document_package_relation_statistics(document_package_id=document_package_id,
                                                             include_collaborations=append_collaborations,
                                                             collaborators_to_filter=collaborators_to_filter))
        elif statistics_type == 'connector':
            return RouteUtil.data_to_json_response(
                DocumentPackageService.
                    get_document_package_connector_statistics(document_package_id=document_package_id,
                                                              include_collaborations=append_collaborations,
                                                              collaborators_to_filter=collaborators_to_filter))
        elif statistics_type == 'summary':
            return RouteUtil.data_to_json_response(
                DocumentPackageService.
                    get_document_package_summary_statistics(document_package_id=document_package_id,
                                                            include_collaborations=append_collaborations,
                                                            collaborators_to_filter=collaborators_to_filter))
        elif statistics_type == 'agreement':

            if statistics_filter == 'all':
                agreement_types = ['tag', 'relation', 'connector']
            else:
                agreement_types = [statistics_filter]

            return RouteUtil.data_to_json_response(
                DocumentPackageService.
                    get_document_package_agreement_statistics(document_package_id=document_package_id,
                                                              collaborators_to_filter=collaborators_to_filter,
                                                              agreement_types=agreement_types))
        elif statistics_type == 'words':

            return RouteUtil.data_to_json_response(
                DocumentPackageService.
                    get_document_package_words_statistics(document_package_id=document_package_id,
                                                          include_collaborations=append_collaborations,
                                                          collaborators_to_filter=collaborators_to_filter))
        else:
            return RouteUtil.data_to_json_response(
                DocumentPackageService.
                    get_document_package_status_statistics(document_package_id=document_package_id,
                                                           include_collaborations=append_collaborations,
                                                           collaborators_to_filter=collaborators_to_filter))


@app.route('/document-package/statistics', methods=['GET'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_packages_statistics():

    document_package_ids = request.args.get('documentPackageIds')

    statistics_type = request.args.get('type')
    statistics_filter = request.args.get('filter')
    append_collaborations = request.args.get('appendCollaborations')
    collaborators_to_filter = request.args.get('collaboratorsToFilter')

    if statistics_type == 'words':

        return RouteUtil.data_to_json_response(
            DocumentPackageService.
                get_document_package_words_statistics(document_package_ids=document_package_ids.split(','),
                                                      include_collaborations=append_collaborations,
                                                      collaborators_to_filter=collaborators_to_filter))


@app.route('/document-package/<document_package_id>/collaboration', methods=['GET', 'POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_package_random_collaboration(document_package_id):

    except_document_id = request.args.get('exceptDocumentId')

    if request.method == 'GET':

        document_package = DocumentPackageService.get_document_package(document_package_id)

        if 'randomAnnotation' in document_package and document_package['randomAnnotation']:
            return RouteUtil.data_to_json_response(DocumentService.get_random_undone_collaboration(
                document_package_id, g.user['email'], except_document_id), True)
        else:
            return RouteUtil.data_to_json_response(DocumentService.get_collaborations(document_package_id, g.user['email'], status='UNDONE'), True)

    elif request.method == 'POST':

        state_key = request.args.get('stateKey')

        state_key = DocumentService.update_collaboration(document_package_id, request.args.get('documentId'),
                                                         g.user['email'], request.json, state_key)

        return state_key, 200


@app.route('/document-package/<document_package_id>/files', methods=['GET'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE'])
@RouteUtil.safe_result()
@RouteUtil.nocache
def document_package_download(document_package_id):

    document_package_found = DocumentPackageService.get_document_package(document_package_id)

    if not document_package_found:
        return 'NOT FOUND', 404

    wanted_status = []

    if RouteUtil.value_to_boolean(request.args.get('includeUnchecked')):
        wanted_status.append('UNCHECKED')
    if RouteUtil.value_to_boolean(request.args.get('includePrechecked')):
        wanted_status.append('PRECHECKED')
    if RouteUtil.value_to_boolean(request.args.get('includeChecked')):
        wanted_status.append('CHECKED')

    documents_zip = DocumentService.get_documents_zip(document_package_id,
                                                      RouteUtil.value_to_boolean(
                                                          request.args.get('includeMetadata')
                                                      ),
                                                      RouteUtil.value_to_boolean(
                                                          request.args.get('includeText')
                                                      ),
                                                      RouteUtil.value_to_boolean(
                                                          request.args.get('includeCollaboration')
                                                      ),
                                                      RouteUtil.value_to_boolean(
                                                          request.args.get('includeStatus')
                                                      ),
                                                      RouteUtil.value_to_boolean(
                                                          request.args.get('includeDescription')
                                                      ),
                                                      RouteUtil.value_to_boolean(
                                                          request.args.get('includeLog')
                                                      ),
                                                      RouteUtil.value_to_boolean(
                                                          request.args.get('includeComments')
                                                      ), wanted_status)

    return make_response(send_file(documents_zip.filename, as_attachment=True, add_etags=False,
                                   attachment_filename=document_package_found['name']+'.zip',
                                   mimetype='application/zip, application/octet-stream'))


'''
var _changeDocumentsStatus = function(documentPackageId, newStatus){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/changeDocumentsStatus', {newStatus: newStatus});
    }

    var _removeDocuments = function(documentPackageId){
    	return $http.delete(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/removeDocuments');
    }

'''


@app.route('/document-package/<document_package_id>/changeDocumentsStatus', methods=['POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE'])
@RouteUtil.safe_result()
def document_package_change_documents_status(document_package_id):

        DocumentPackageService.change_documents_status(document_package_id, RouteUtil.safe_json_get('newStatus'))
        return 'OK', 200


@app.route('/document-package/<document_package_id>/removeDocuments', methods=['DELETE'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE'])
@RouteUtil.safe_result()
def document_package_remove_documents(document_package_id):

        DocumentService.remove_documents_by_document_packages([document_package_id])
        return 'OK', 200


@app.route('/document-package/<document_package_id>/changeCollaborationsStatus', methods=['POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE'])
@RouteUtil.safe_result()
def document_package_change_collaborations_status(document_package_id):

        DocumentPackageService.update_collaborations_status(document_package_id, g.user['email'],
                                                            RouteUtil.safe_json_get('collaboratorEmail'),
                                                            RouteUtil.safe_json_get('newStatus'))
        return 'OK', 200


@app.route('/document-package/<document_package_id>/comments', methods=['GET'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_package_comments(document_package_id):

    return RouteUtil.data_to_json_response(DocumentPackageService.get_document_package_comments(document_package_id))