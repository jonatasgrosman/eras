import module.service.documentService as DocumentService
import module.util.routeUtil as RouteUtil
from flask import request, g, make_response, send_file
from module import app
import tempfile


@app.route('/document', methods=['GET', 'POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document_root():

    project_id = request.args.get('projectId')
    document_package_id = request.args.get('documentPackageId')
    status = request.args.get('status')
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    append_document_package_detail = RouteUtil.value_to_boolean(request.args.get('appendDocumentPackageDetail'))
    append_collaborator_detail = RouteUtil.value_to_boolean(request.args.get('appendCollaboratorDetail'))

    if request.method == 'GET':

        return RouteUtil.data_to_json_response(DocumentService.get_documents(project_id, document_package_id,
                                                                             status, skip, limit,
                                                                             append_document_package_detail,
                                                                             append_collaborator_detail))

    elif request.method == 'POST':

        return DocumentService.insert_document(document_package_id, RouteUtil.safe_json_get('text'),
                                               RouteUtil.safe_json_get('name'), RouteUtil.safe_json_get('isPlainText'))


@app.route('/document/<document_id>', methods=['GET', 'POST', 'DELETE'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def document(document_id):

    as_file = RouteUtil.value_to_boolean(request.args.get('asFile'))

    if request.method == 'GET':

        if as_file:

            found_document = DocumentService.get_document(document_id, append_document_package_detail=False,
                                                          append_collaborator_detail=False, log_document_open=False)

            if not found_document:
                return 'NOT FOUND', 404

            '''
            document_text = DocumentService.get_document_as_text(found_document)

            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(document_text.encode('utf-8'))
            temp_file.flush()
            temp_file.seek(0)
            '''

            document_file = DocumentService.get_document_as_file(found_document, None,
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
                                                                 ))

            return make_response(send_file(document_file.name, as_attachment=True, add_etags=False,
                                           attachment_filename=found_document['name'], mimetype='text/plain',
                                           cache_timeout=10))
        else:
            return RouteUtil.data_to_json_response(DocumentService.get_document(document_id), True)

    elif request.method == 'POST':

        using_change_log = RouteUtil.value_to_boolean(request.args.get('usingChangeLog'))
        state_key = request.args.get('stateKey')

        if using_change_log:
            lock_token = DocumentService.get_document_lock(document_id)
            state_key = DocumentService.update_document_by_log(document_id, request.json, lock_token, state_key)
            DocumentService.release_document_lock(lock_token, document_id)
            return state_key, 201
        else:
            DocumentService.update_document(document_id, request.json['name'], request.json['metadata'])
            return 'OK', 201

    elif request.method == 'DELETE':
        DocumentService.remove_document(document_id)
        return 'OK', 201


@app.route('/document/<document_id>/collaboration/status', methods=['POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE'])
@RouteUtil.safe_result()
def document_collaboration_status(document_id):

    DocumentService.update_collaboration_status(document_id, g.user['email'],
                                                RouteUtil.safe_json_get('collaboratorEmail'),
                                                RouteUtil.safe_json_get('status'))
    return 'OK', 201
