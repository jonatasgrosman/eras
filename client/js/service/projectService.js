angular.module('ERAS').factory('ProjectService',
['$http', '$q', 'Constants', 'HttpUtil', 'LocalStorageService',
function($http, $q, Constants, HttpUtil, LocalStorageService) {

    var _insert = function(project){
    	return $http.post(Constants.DATA_SERVER_URL + '/project', project);
    }

    var _remove = function(projectId){
    	return $http.delete(Constants.DATA_SERVER_URL + '/project/'+projectId);
    }

    var _update = function(project){
        return $http.post(Constants.DATA_SERVER_URL + '/project/'+project.id, project);
    }

    var _updateEntities = function(projectId, entities){
        return $http.post(Constants.DATA_SERVER_URL + '/project/'+projectId+'/entities', entities);
    }

    var _get = function(projectId, appendStatistics){
        var url = Constants.DATA_SERVER_URL + '/project/'+projectId;

        if(appendStatistics){
            url = HttpUtil.addParameter(url, 'appendStatistics', true)
        }

        return $http.get(url);
    }

    var _list = function(appendStatistics){
        var url = Constants.DATA_SERVER_URL + '/project';

        if(appendStatistics){
            url = HttpUtil.addParameter(url, 'appendStatistics', true)
        }

        return $http.get(url);
    }

    var _getOntologyFile = function(project){
        return $http({
            url: Constants.DATA_SERVER_URL +'/project/'+project.id+'/ontology',
            method: 'GET',
            responseType: 'arraybuffer',
            cache: false,
            headers: {
              'Content-Type': project.ontology.type
            }
        });
    }

    var _uploadOntologyFile = function(projectId, ontology){
    	return $http.post(Constants.DATA_SERVER_URL +'/project/'+projectId+'/ontology', ontology);
    }

    var _getAnnotationGuidelinesFile = function(project){
        return $http({
            url: Constants.DATA_SERVER_URL +'/project/'+project.id+'/annotation-guidelines',
            method: 'GET',
            responseType: 'arraybuffer',
            cache: false,
            headers: {
              'Content-Type': project.annotationGuidelines.type
            }
        });
    }

    var _getOntologyStructure = function(projectId){
    	return $http.get(Constants.DATA_SERVER_URL +'/project/'+projectId+'/ontology?type=summary');
    }

    var _getOntologyTree = function(projectId){
        return $http.get(Constants.DATA_SERVER_URL +'/project/'+projectId+'/ontology?type=tree');
    }

    var _getOntologyStructureFromFile = function(ontologyFile){
    	return $http.post(Constants.DATA_SERVER_URL +'/ontology-summary', ontologyFile);
    }

    var _getAnnotationGuidelinesFileUrl = function(projectId){
        var user = LocalStorageService.get(Constants.USER_STORAGE_KEY);
        return Constants.DATA_SERVER_URL +'/project/'+projectId+'/annotation-guidelines?email='+user.email+'&token='+user.token;
    }

    var _uploadAnnotationGuidelinesFile = function(projectId, annotationGuidelines){
    	return $http.post(Constants.DATA_SERVER_URL +'/project/'+projectId+'/annotation-guidelines', annotationGuidelines);
    }

    var _removeAnnotationGuidelinesFile = function(projectId){
    	return $http.delete(Constants.DATA_SERVER_URL +'/project/'+projectId+'/annotation-guidelines');
    }

    var _getOntologyMap = function(projectId){
        return $http.get(Constants.DATA_SERVER_URL +'/project/'+projectId+'/ontology?type=map');

        /*var deferred = $q.defer();
        _getOntologyStructure(projectId).then(function(response){

            var ontologyStructure = response.data;
            var ontologyMap = {}
            var cardinalityMap = {}

            //console.info(ontologyStructure);

            var getlevel = function(entity){
                if(entity.parent == 'Thing' || entity.parent == 'DataType'){
                    return 0;
                }else{
                    parent = ontologyStructure.Class[entity.parent];
                    return 1+getlevel(parent);
                }
            }

            entitiesName = Object.keys(ontologyStructure.Class).sort(function(a, b){
                var aLevel = getlevel(ontologyStructure.Class[a]);
                var bLevel = getlevel(ontologyStructure.Class[b])
                return bLevel-aLevel;
            });

            //CREATING DESCENDANTS MAP
            var descendantsByEntity = {}
            angular.forEach(entitiesName, function(entityName){

                var entity = ontologyStructure.Class[entityName];

                cardinalityMap[entityName] = {}

                angular.forEach(entity.domain, function(relation){
                    cardinalityMap[entityName][relation.property] = relation.max;
                });

                if(entity.parent && entity.parent != 'Thing' && entity.parent != 'DataType'){
                    if(!descendantsByEntity[entity.parent]){
                        descendantsByEntity[entity.parent] = {};
                    }
                    descendantsByEntity[entity.parent][entityName] = true;

                    if(descendantsByEntity[entityName]){
                        angular.forEach(Object.keys(descendantsByEntity[entityName]), function(descendant){
                            descendantsByEntity[entity.parent][descendant] = true;
                        });
                    }
                }

            });

            //console.info(descendantsByEntity);

            entitiesName.reverse();

            var relationsByDomain = {}
            var enumeratorsByEntity = {}

            //CREATING DATAPROPERTY MAP
            angular.forEach(Object.keys(ontologyStructure.DataProperty), function(property){
                var dataProperty = ontologyStructure.DataProperty[property];
                angular.forEach(dataProperty.domain, function(domain){
                    var relations = relationsByDomain[domain];
                    if(!relations){
                        relations = [];
                        relationsByDomain[domain] = relations;
                    }
                    angular.forEach(dataProperty.range, function(range){
                        relations.push({range:range, property:property});
                    });
                });
            });

            //CREATING OBJECTPROPERTY MAP
            angular.forEach(Object.keys(ontologyStructure.ObjectProperty), function(property){
                var objectProperty = ontologyStructure.ObjectProperty[property];
                angular.forEach(objectProperty.domain, function(domain){
                    var relations = relationsByDomain[domain];
                    if(!relations){
                        relations = [];
                        relationsByDomain[domain] = relations;
                    }
                    angular.forEach(objectProperty.range, function(range){
                        relations.push({range:range, property:property});
                    });
                });
            });

            //CREATING ENUMERATORS MAP
            angular.forEach(Object.keys(ontologyStructure.Enumerator), function(entity){
                enumeratorsByEntity[entity] = ontologyStructure.Enumerator[entity];
            });

            angular.forEach(entitiesName, function(entityName){

                var entity = ontologyStructure.Class[entityName];

                ontologyMap[entityName] = {}

                relations = relationsByDomain[entityName];
                if(relations){
                    angular.forEach(relations, function(relation){

                        var relationDescriptor = {targets:[]}
                        var maxCardinality = cardinalityMap[entityName][relation.property];
                        if(maxCardinality){
                            relationDescriptor.max = parseInt(maxCardinality);
                        }
                        ontologyMap[entityName][relation.property] = relationDescriptor;

                        var enumerators = enumeratorsByEntity[relation.range];
                        if(enumerators){
                            angular.forEach(enumerators, function(enumerator){
                                relationDescriptor.targets.push(relation.range+':'+enumerator);
                            });
                        }else{
                            relationDescriptor.targets.push(relation.range);

                            if(descendantsByEntity[relation.range]){
                                angular.forEach(Object.keys(descendantsByEntity[relation.range]), function(descendant){
                                    relationDescriptor.targets.push(descendant);
                                });
                            }
                        }
                    });
                }

                if(entity.parent && entity.parent != 'Thing' && entity.parent != 'DataType'){
                    angular.forEach(Object.keys(ontologyMap[entity.parent]), function(property){
                        ontologyMap[entityName][property] = ontologyMap[entity.parent][property]
                    });
                }

                var enumerators = enumeratorsByEntity[entityName];
                if(enumerators){
                    angular.forEach(enumerators, function(enumerator){
                        ontologyMap[entityName+':'+enumerator] = angular.copy(ontologyMap[entityName]);
                    });
                    delete ontologyMap[entityName];
                }

            });

            response.data = ontologyMap;

            deferred.resolve(response);
        },function(response){
            deferred.reject(response);
        });

        return deferred.promise;*/
    };

    return {
        insert : _insert,
        remove : _remove,
        update : _update,
        updateEntities: _updateEntities,
    	get : _get,
    	list : _list,
    	getOntologyFile : _getOntologyFile,
        getOntologyTree: _getOntologyTree,
    	getOntologyStructure : _getOntologyStructure,
    	getOntologyStructureFromFile : _getOntologyStructureFromFile,
    	uploadOntologyFile : _uploadOntologyFile,
    	getAnnotationGuidelinesFile : _getAnnotationGuidelinesFile,
    	uploadAnnotationGuidelinesFile : _uploadAnnotationGuidelinesFile,
    	removeAnnotationGuidelinesFile : _removeAnnotationGuidelinesFile,
    	getOntologyMap : _getOntologyMap,
    	getAnnotationGuidelinesFileUrl : _getAnnotationGuidelinesFileUrl
    }

}]);
