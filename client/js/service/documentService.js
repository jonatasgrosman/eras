angular.module('ERAS').factory('DocumentService',
['$http', 'Constants', 'HttpUtil',
function($http, Constants, HttpUtil) {

    var _insert = function(documentPackageId, document){
    	return $http.post(Constants.DATA_SERVER_URL + '/document?documentPackageId='+documentPackageId, document);
    }

    var _update = function(document, changeLog){
        if(!changeLog){
    	    return $http.post(Constants.DATA_SERVER_URL + '/document/'+document.id, {
    	        name: document.name, metadata: document.metadata
            });
        }else{
            return $http.post(Constants.DATA_SERVER_URL + '/document/'+document.id+'?usingChangeLog=true&stateKey='+document.stateKey, changeLog);
        }
    }

    var _remove = function(documentId){
    	return $http.delete(Constants.DATA_SERVER_URL + '/document/'+documentId);
    }

    var _get = function(documentId, asFile, includeMetadata, includeText, includeCollaboration, includeStatus,
                        includeDescription, includeLog, includeComments){

        var url = Constants.DATA_SERVER_URL + '/document/'+documentId+'?asFile='+asFile;
        url += '&includeMetadata='+includeMetadata;
        url += '&includeText='+includeText;
        url += '&includeCollaboration='+includeCollaboration;
        url += '&includeStatus='+includeStatus;
        url += '&includeDescription='+includeDescription;
        url += '&includeLog='+includeLog;
        url += '&includeComments='+includeComments;

        return $http.get(url);
    }

    var _list = function(projectId, documentPackageId, skip, limit, status, appendDocumentPackageDetail, appendCollaboratorDetail){

        var url = Constants.DATA_SERVER_URL + '/document';

        if(projectId){
            url = HttpUtil.addParameter(url, 'projectId', projectId)
        }
        if(documentPackageId){
            url = HttpUtil.addParameter(url, 'documentPackageId', documentPackageId)
        }
        if(skip){
            url = HttpUtil.addParameter(url, 'skip', skip)
        }
        if(limit){
            url = HttpUtil.addParameter(url, 'limit', limit)
        }
        if(status){
            url = HttpUtil.addParameter(url, 'status', status)
        }
        if(appendDocumentPackageDetail){
            url = HttpUtil.addParameter(url, 'appendDocumentPackageDetail', appendDocumentPackageDetail)
        }
        if(appendCollaboratorDetail){
            url = HttpUtil.addParameter(url, 'appendCollaboratorDetail', appendCollaboratorDetail)
        }

    	return $http.get(url);
    }

    var _updateCollaborationStatus = function(documentId, collaboratorEmail, status){
    	return $http.post(Constants.DATA_SERVER_URL + '/document/'+documentId+'/collaboration/status',
    	                    {collaboratorEmail:collaboratorEmail, status:status});
    }

    /*var _insertCollaborator = function(documentPackageId, collaborator){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/collaborator', collaborator);
    }

    var _removeCollaborator = function(documentPackageId, collaborator){
    	return $http.delete(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/collaborator?email='+collaborator.email);
    }




    //REVER below
    var _listByCollaborator = function(collaborator){
    	return $http.get(Constants.DATA_SERVER_URL + '/document-package?email='+collaborator.email);
    }



    var _insertDocument = function(project, documentPackage, document){
    	return $http.post(Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/document', document);
    }

    var _updateDocument = function(project, documentPackage, document){
    	return $http.post(Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/document'+'?id='+document.id.$oid, document);
    }

    var _removeDocument = function(project, documentPackage, document){
    	return $http.delete(Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/document'+'?id='+document.id.$oid);
    }

    var _getDocument = function(project, documentPackage, id){
    	return $http.get(Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/document?id='+id);
    }

    var _listDocuments = function(project, documentPackage, skip, limit, status){
        var url = Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/document';
        if(skip){
            url += '?skip='+skip;
        }
        if(limit){
            url += skip ? '&limit=' + limit : '?limit=' + limit;
        }
        if(status){
            url += limit ? '&status='+ status : '?status=' + status;
        }
    	return $http.get(url);
    }

    var _listCollaborations = function(project, documentPackage, document){
        return $http.get(Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/document/'+document.id.$oid+'/collaboration');
    }

    var _getRandomUndoneCollaboration = function(project, documentPackage, collaborator, exceptDocument){
        var url = Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/random-undone-collaboration?email='+collaborator.email;
        if(exceptDocument){
            url += '&except='+exceptDocument.id.$oid;
        }
    	return $http.get(url);
    }

    var _getCollaboration = function(project, documentPackage, document, collaborator){
        return $http.get(Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/document/'+document.id.$oid+'/collaboration?email='+collaborator.email);
    }

    var _updateCollaboration = function(project, documentPackage, document, collaborator, collaboration, isReannotation){
    	return $http.post(Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/document/'+document.id.$oid+'/collaboration?email='+collaborator.email+'&isReannotation='+isReannotation, collaboration);
    }

    var _getStatistics = function(project, documentPackage, documentStatus){
        var url = Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/statistics';
        if(documentStatus){
            url += '?documentStatus='+documentStatus;
        }
    	return $http.get(url);
    }

    var _getCollaboratorStatistics = function(project, documentPackage, collaborator){
    	return $http.get(Constants.DATA_SERVER_URL + '/project/'+project.id.$oid+'/document-package/'+documentPackage.id+'/statistics?email='+collaborator.email);
    }*/

    return {
        insert : _insert,
        remove : _remove,
    	update : _update,
    	get : _get,
    	list : _list,
    	updateCollaborationStatus : _updateCollaborationStatus
    	/*listByCollaborator : _listByCollaborator,
    	insertCollaborator : _insertCollaborator,
    	removeCollaborator : _removeCollaborator,
    	insertDocument : _insertDocument,
    	updateDocument : _updateDocument,
    	removeDocument : _removeDocument,
    	getDocument : _getDocument,
    	listDocuments : _listDocuments,
    	listCollaborations : _listCollaborations,
    	getRandomUndoneCollaboration : _getRandomUndoneCollaboration,
    	getCollaboration : _getCollaboration,
    	updateCollaboration : _updateCollaboration,
    	getStatistics : _getStatistics,
    	getCollaboratorStatistics : _getCollaboratorStatistics*/
    }

}]);
