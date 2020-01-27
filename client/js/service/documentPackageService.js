angular.module('ERAS').factory('DocumentPackageService',
['$http', 'Constants', 'HttpUtil',
function($http, Constants, HttpUtil) {

    var _insert = function(documentPackage){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package', documentPackage);
    }

    var _update = function(documentPackage){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackage.id, documentPackage);
    }

    var _remove = function(documentPackageId){
    	return $http.delete(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId);
    }

    var _get = function(documentPackageId){
        return $http.get(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId);
    }

    var _listByCollaborator = function(collaborator){
    	return $http.get(Constants.DATA_SERVER_URL + '/document-package?collaboratorEmail='+collaborator.email);
    }

    var _insertCollaborator = function(documentPackageId, collaborator){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/collaborator', collaborator);
    }

    var _updateCollaborator = function(documentPackageId, collaborator){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/collaborator?email='+collaborator.email, collaborator);
    }

    var _removeCollaborator = function(documentPackageId, collaboratorEmail){
    	return $http.delete(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/collaborator?email='+collaboratorEmail);
    }

    var _listGroups = function(documentPackageId){
    	return $http.get(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/group');
    }

    var _getGroupByCollaboratorEmail = function(documentPackageId, collaboratorEmail){
    	return $http.get(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/group?collaboratorEmail='+collaboratorEmail);
    }

    var _insertGroup = function(documentPackageId, group){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/group', group);
    }

    var _updateGroup = function(documentPackageId, group){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/group?groupId='+group.id, group);
    }

    var _removeGroup = function(documentPackageId, groupId){
    	return $http.delete(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/group?groupId='+groupId);
    }

    var _changeDocumentsStatus = function(documentPackageId, newStatus){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/changeDocumentsStatus', {newStatus: newStatus});
    }

    var _changeCollaborationsStatus = function(documentPackageId, collaboratorEmail, newStatus){
    	return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/changeCollaborationsStatus', {newStatus: newStatus, collaboratorEmail: collaboratorEmail});
    }

    var _removeDocuments = function(documentPackageId){
    	return $http.delete(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/removeDocuments');
    }

    var _getStatistics = function(documentPackageId, collaboratorEmail, type, appendCollaborations, collaboratorsToFilter, filter, documentPackageIds, appendAgreement){

        if(documentPackageId){
            var url = Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/statistics'
        }else{
            var url = Constants.DATA_SERVER_URL + '/document-package/statistics';
            if(documentPackageIds){
                url = HttpUtil.addParameter(url, 'documentPackageIds', documentPackageIds.join(','));
            }
        }

        if(appendAgreement){
            url = HttpUtil.addParameter(url, 'appendAgreement', appendAgreement)
        }

        if(type){
            url = HttpUtil.addParameter(url, 'type', type)
        }
        if(filter){
            url = HttpUtil.addParameter(url, 'filter', filter)
        }
        if(collaboratorEmail){
            url = HttpUtil.addParameter(url, 'collaboratorEmail', collaboratorEmail)
        }else{
            if(appendCollaborations){
                url = HttpUtil.addParameter(url, 'appendCollaborations', true);
                if(collaboratorsToFilter){
                    url = HttpUtil.addParameter(url, 'collaboratorsToFilter', collaboratorsToFilter.join());
                }
            }
        }

    	return $http.get(url);
    }

    var _getCollaboration = function(documentPackageId, exceptDocumentId){

        var url = Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/collaboration'

        if(exceptDocumentId){
            url = HttpUtil.addParameter(url, 'exceptDocumentId', exceptDocumentId)
        }

    	return $http.get(url);
    }

    var _updateCollaboration = function(documentPackageId, collaboration, changeLog){
        return $http.post(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/collaboration?documentId='+collaboration.id+'&stateKey='+collaboration.stateKey, changeLog);
    }

    var _getDocumentsZip = function(documentPackageId, includeUnchecked, includePrechecked, includeChecked,
                                    includeMetadata, includeText, includeCollaboration, includeStatus,
                                    includeDescription, includeLog, includeComments){

        var url = Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/files?';
        url += 'includeUnchecked='+includeUnchecked;
        url += '&includePrechecked='+includePrechecked;
        url += '&includeChecked='+includeChecked;
        url += '&includeMetadata='+includeMetadata;
        url += '&includeText='+includeText;
        url += '&includeCollaboration='+includeCollaboration;
        url += '&includeStatus='+includeStatus;
        url += '&includeDescription='+includeDescription;
        url += '&includeLog='+includeLog;
        url += '&includeComments='+includeComments;

        return $http({
            url: url,
            method: 'GET',
            responseType: 'arraybuffer',
            cache: false,
            headers: {
              'Content-Type': 'application/zip, application/octet-stream'
            }
        });
    }

    var _getComments = function(documentPackageId){
        return $http.get(Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/comments');
    }

    /*var _getStatusStatistics = function(documentPackageId, collaboratorsToFilter, appendCollaborations){

        var url = Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/statistics/status';

        if(appendCollaborations){
            url = HttpUtil.addParameter(url, 'appendCollaborations', true);
            if(collaboratorsToFilter){
                url = HttpUtil.addParameter(url, 'collaboratorsToFilter', collaboratorsToFilter.join());
            }
        }
        return $http.get(url);
    };

    var _getTagStatistics = function(documentPackageId, collaboratorsToFilter, appendCollaborations){

        var url = Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/statistics/tag';

        if(appendCollaborations){
            url = HttpUtil.addParameter(url, 'appendCollaborations', true);
            if(collaboratorsToFilter){
                url = HttpUtil.addParameter(url, 'collaboratorsToFilter', collaboratorsToFilter.join());
            }
        }
        return $http.get(url);
    };

    var _getRelationStatistics = function(documentPackageId, collaboratorsToFilter, appendCollaborations){

        var url = Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/statistics/relation';

        if(appendCollaborations){
            url = HttpUtil.addParameter(url, 'appendCollaborations', true);
            if(collaboratorsToFilter){
                url = HttpUtil.addParameter(url, 'collaboratorsToFilter', collaboratorsToFilter.join());
            }
        }
        return $http.get(url);
    };

    var _getConnectorStatistics = function(documentPackageId, collaboratorsToFilter, appendCollaborations){

        var url = Constants.DATA_SERVER_URL + '/document-package/'+documentPackageId+'/statistics';

        if(appendCollaborations){
            url = HttpUtil.addParameter(url, 'appendCollaborations', true);
            if(collaboratorsToFilter){
                url = HttpUtil.addParameter(url, 'collaboratorsToFilter', collaboratorsToFilter.join());
            }
        }
        return $http.get(url);
    };*/

    return {
        insert : _insert,
        remove : _remove,
    	update : _update,
    	get : _get,
    	listByCollaborator : _listByCollaborator,
    	insertCollaborator : _insertCollaborator,
    	updateCollaborator : _updateCollaborator,
    	removeCollaborator : _removeCollaborator,
    	listGroups : _listGroups,
    	getGroupByCollaboratorEmail : _getGroupByCollaboratorEmail,
    	insertGroup : _insertGroup,
    	updateGroup : _updateGroup,
    	removeGroup : _removeGroup,
    	getStatistics : _getStatistics,
    	changeDocumentsStatus : _changeDocumentsStatus,
    	changeCollaborationsStatus : _changeCollaborationsStatus,
    	removeDocuments : _removeDocuments,
    	getCollaboration : _getCollaboration,
    	updateCollaboration : _updateCollaboration,
    	getDocumentsZip : _getDocumentsZip,
        getComments: _getComments/*,
        getStatusStatistics: _getStatusStatistics,
        getTagStatistics: _getTagStatistics,
        getRelationStatistics: _getRelationStatistics,
        getConnectorStatistics: _getConnectorStatistics*/
    }

}]);
