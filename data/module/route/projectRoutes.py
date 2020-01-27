import base64
import module.service.projectService as ProjectService
import module.util.routeUtil as RouteUtil
from flask import request, g, make_response, send_file
from module import app


@app.route('/project', methods=['GET', 'POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def project_root():

    skip = request.args.get('skip')
    limit = request.args.get('limit')
    append_statistics = RouteUtil.value_to_boolean(request.args.get('appendStatistics'))

    if request.method == 'GET':
        return RouteUtil.data_to_json_response(
            ProjectService.get_projects(g.user['email'], skip=skip, limit=limit,
                                        append_documents_package_statistics=append_statistics))

    elif request.method == 'POST':

        if 'ontology' not in request.json:
            return 'ONTOLOGY IS REQUIRED', 400

        _, b64data = request.json['ontology']['data'].split(',')
        request.json['ontology']['bytes'] = base64.b64decode(b64data)

        if 'annotationGuidelines' in request.json:
            _, b64data = request.json['annotationGuidelines']['data'].split(',')
            request.json['annotationGuidelines']['bytes'] = base64.b64decode(b64data)

        return ProjectService.create_project(g.user['email'],
                                             RouteUtil.safe_json_get('name'),
                                             RouteUtil.safe_json_get('language'),
                                             RouteUtil.safe_json_get('smartSentenceSegmentation'),
                                             RouteUtil.safe_json_get('smartWordSegmentation'),
                                             RouteUtil.safe_json_get('textReplacements'),
                                             RouteUtil.safe_json_get('ontology'),
                                             RouteUtil.safe_json_get('annotationGuidelines'))


@app.route('/project/<project_id>', methods=['GET', 'POST', 'DELETE'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def project(project_id):

    append_statistics = RouteUtil.value_to_boolean(request.args.get('appendStatistics'))

    if request.method == 'GET':
        return RouteUtil.data_to_json_response(ProjectService.get_project(project_id, True, append_statistics), True)

    elif request.method == 'POST':
        ProjectService.update_project(project_id, RouteUtil.safe_json_get('name'),
                                      RouteUtil.safe_json_get('smartSentenceSegmentation'),
                                      RouteUtil.safe_json_get('smartWordSegmentation'),
                                      RouteUtil.safe_json_get('textReplacements'))
        return 'OK', 200

    elif request.method == 'DELETE':
        ProjectService.remove_project(project_id)
        return 'OK', 200


@app.route('/project/<project_id>/entities', methods=['POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE'])
@RouteUtil.safe_result()
def project_entities(project_id):
    
    ProjectService.update_project_entities(project_id, request.json)
    return 'OK', 200


@app.route('/project/<project_id>/ontology', methods=['GET', 'POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
@RouteUtil.nocache
def ontology(project_id):

    ontology_type = request.args.get('type')

    if request.method == 'GET':

        if ontology_type == 'map':
            return RouteUtil.data_to_json_response(ProjectService.get_ontology_map(project_id))
        elif ontology_type == 'tree':
            return RouteUtil.data_to_json_response(ProjectService.get_ontology_tree(project_id))
        elif ontology_type == 'summary':
            return RouteUtil.data_to_json_response(ProjectService.get_ontology_summary(project_id))
        else:
            project_ontology = ProjectService.get_ontology(project_id)
            if project_ontology:
                return make_response(send_file(project_ontology,
                                               as_attachment=False,
                                               add_etags=False,
                                               attachment_filename=project_ontology.name,
                                               mimetype=project_ontology.contentType))
            return 'NOT FOUND', 404

    elif request.method == 'POST':
        if request.json:

            _, b64data = request.json['data'].split(',')
            request.json['bytes'] = base64.b64decode(b64data)

            return ProjectService.update_project_ontology(project_id, request.json), 201

        return 'CHECK THE INPUT', 400


@app.route('/project/<project_id>/annotation-guidelines', methods=['GET', 'POST', 'DELETE'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
@RouteUtil.nocache
def annotation_guidelines(project_id):

    if request.method == 'GET':
        project_annotation_guidelines = ProjectService.get_annotation_guidelines(project_id)

        if project_annotation_guidelines:
            return make_response(send_file(project_annotation_guidelines,
                                           as_attachment=False,
                                           add_etags=False,
                                           attachment_filename=project_annotation_guidelines.name,
                                           mimetype=project_annotation_guidelines.contentType))
        return 'NOT FOUND', 404

    elif request.method == 'POST':
        if request.json:
            _, b64data = request.json['data'].split(',')
            request.json['bytes'] = base64.b64decode(b64data)

            return ProjectService.update_annotation_guidelines(project_id, request.json), 201

        return 'CHECK THE INPUT', 400

    elif request.method == 'DELETE':
        ProjectService.remove_annotation_guidelines(project_id)

        return 'OK', 200
