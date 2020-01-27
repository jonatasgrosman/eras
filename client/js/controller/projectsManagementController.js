angular.module('ERAS').controller('ProjectsManagementController',
    ['$scope', '$http', 'blockUI', 'PNotifyUtil', 'ArrayUtil', 'ProjectService', 'OntologyUtil',
    function($scope, $http, blockUI, PNotifyUtil, ArrayUtil, ProjectService, OntologyUtil) {

	$scope.init = function() {
        $scope.projectsManagementBoxBlockUI = blockUI.instances.get('projectsManagementBox');
        $scope.listProjects();
        $scope.languages = [{label:'Portuguese (BR)',value:'pt-br'},{label:'English (US)',value:'en-us'}];
        $scope.selection = {}
    }

	$scope.onShowOntologyUploadModal = function(project){
	    $scope.selection.project = project;
	    $scope.selection.ontology = null;
	}

	$scope.onShowAnnotationGuidelinesUploadModal = function(project){
	    $scope.selection.project = project;
	    $scope.selection.annotationGuidelines = null;
	}

	$scope.onShowAddProjectModal = function() {
	    $scope.originalProject = null;
	    $scope.isEditMode = false;
	    $scope.project = {textReplacements:[], smartWordSegmentation:false, smartSentenceSegmentation:false}
	}

    $scope.onShowEditProjectModal = function(project) {
        $scope.originalProject = project;
        $scope.isEditMode = true;
        $scope.project = angular.copy(project);
    }

    $scope.onShowAnnotationGuidelinesModal = function(project) {
        PDFObject.embed(ProjectService.getAnnotationGuidelinesFileUrl(project.id), "#annotationGuidelinesPdfContainer");
	}

	$scope.onShowOntologyModal = function(project){

        $scope.selection.project = angular.copy(project);

	    /*$scope.ontologyEntityTree = [];
        $scope.ontologyRelationTree = [];

	    $scope.projectsManagementBoxBlockUI.start();
        ProjectService.getOntologyTree(project.id).then(function(response) {

            $scope.ontologyEntityTree = OntologyUtil.getTree(response.data, 'entity');
            $scope.ontologyRelationTree = OntologyUtil.getTree(response.data, 'relation', true);

        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.projectsManagementBoxBlockUI.stop();
        });*/
    }

    $scope.updateProjectEntities = function() {
        ProjectService.updateEntities($scope.selection.project.id, $scope.selection.project.entities).then(function(response) {
            PNotifyUtil.showSuccess(':)', 'Project entities updated');
            $scope.listProjects();
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
            console.info(response);
        }).finally(function(){
            $scope.projectsManagementBoxBlockUI.stop();
        });
    }

	$scope.addReplacement = function() {
	    $scope.project.textReplacements.push({pattern:'', value:''});
	}

	$scope.removeReplacement = function(replacement) {
	    ArrayUtil.remove($scope.project.textReplacements, replacement);
	}

	$scope.listProjects = function() {
	    $scope.projectsManagementBoxBlockUI.start();
		ProjectService.list().then(function(response) {
		    $scope.projects = response.data;
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.projectsManagementBoxBlockUI.stop();
        });
	}

	$scope.downloadOntology = function(project){
	    $scope.projectsManagementBoxBlockUI.start();
        ProjectService.getOntologyFile(project).then(function(response) {
            var blob = new Blob([response.data], {type: project.ontology.type});
            saveAs(blob, project.ontology.name);
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.projectsManagementBoxBlockUI.stop();
        });
	}

	$scope.uploadOntology = function(){

        $scope.projectsManagementBoxBlockUI.start();
	    ProjectService.getOntologyStructureFromFile(
           $scope.selection.ontology
        ).then(function(response) {
		    ProjectService.uploadOntologyFile($scope.selection.project.id, $scope.selection.ontology).then(function(response) {
                PNotifyUtil.showSuccess(':)', 'Ontology uploaded');
                $scope.listProjects();
            }, function(response) {
                PNotifyUtil.showError(':(', 'Something unexpected happened');
            }).finally(function(){
                $scope.projectsManagementBoxBlockUI.stop();
            });
        }, function(response) {
            PNotifyUtil.showError(':(', 'Invalid ontology file');
        	$scope.projectsManagementBoxBlockUI.stop();
        });

	}

	$scope.downloadAnnotationGuidelines = function(project){
	    $scope.projectsManagementBoxBlockUI.start();
        ProjectService.getAnnotationGuidelinesFile(project).then(function(response) {
            var blob = new Blob([response.data], {type: project.annotationGuidelines.type});
            saveAs(blob, project.annotationGuidelines.name);
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.projectsManagementBoxBlockUI.stop();
        });
	}

	$scope.uploadAnnotationGuidelines = function(){
	    $scope.projectsManagementBoxBlockUI.start();
        ProjectService.uploadAnnotationGuidelinesFile($scope.selection.project.id, $scope.selection.annotationGuidelines).then(function(response) {
            PNotifyUtil.showSuccess(':)', 'Annotation guidelines uploaded');
            $scope.listProjects();
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.projectsManagementBoxBlockUI.stop();
        });
	}

	$scope.removeAnnotationGuidelines = function(project){
	    $scope.projectsManagementBoxBlockUI.start();
        ProjectService.removeAnnotationGuidelinesFile(project.id).then(function(response) {
            PNotifyUtil.showSuccess(':)', 'Annotation guidelines removed');
            $scope.listProjects();
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.projectsManagementBoxBlockUI.stop();
        });
	}

    $scope.removeProject = function(project) {
        $scope.projectsManagementBoxBlockUI.start();
        ProjectService.remove(project.id).then(function(response) {
            ArrayUtil.remove($scope.projects, project);
            PNotifyUtil.showSuccess(':)', 'Project removed');
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.projectsManagementBoxBlockUI.stop();
        });
    }

    $scope.saveProject = function() {

        $scope.projectsManagementBoxBlockUI.start();
        angular.element('#projectModal').modal('hide');

        if(!$scope.isEditMode){
            ProjectService.getOntologyStructureFromFile(
               $scope.project.ontology
            ).then(function(response) {
                ProjectService.insert($scope.project).then(function(response) {
                    PNotifyUtil.showSuccess(':)', 'Project added');
                    $scope.listProjects();
                }, function(response) {
                    PNotifyUtil.showError(':(', 'Something unexpected happened');
                    console.info(response);
                }).finally(function(){
                    $scope.originalProject = null;
                    $scope.project = null;
                    $scope.projectsManagementBoxBlockUI.stop();
                });
            }, function(response) {
                PNotifyUtil.showError(':(', 'Invalid ontology file');
                $scope.projectsManagementBoxBlockUI.stop();
            });
        }else{
            ProjectService.update($scope.project).then(function(response) {
                PNotifyUtil.showSuccess(':)', 'Project updated');
                $scope.listProjects();
            }, function(response) {
                PNotifyUtil.showError(':(', 'Something unexpected happened');
                console.info(response);
            }).finally(function(){
                $scope.originalProject = null;
                $scope.project = null;
                $scope.projectsManagementBoxBlockUI.stop();
            });
        }

    }

    $scope.init();

}]);
