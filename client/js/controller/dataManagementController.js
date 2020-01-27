angular.module('ERAS').controller('DataManagementController',
    ['$scope', '$document', '$timeout', 'blockUI', 'PNotifyUtil', 'ArrayUtil', 'StatisticsUtil', 'DateUtil', 'Base64Util', 'PlotlyUtil', 'ProjectService', 'DocumentPackageService', 'DocumentService', 'LatexUtil',
    function($scope, $document, $timeout, blockUI, PNotifyUtil, ArrayUtil, StatisticsUtil, DateUtil, Base64Util, PlotlyUtil, ProjectService, DocumentPackageService, DocumentService, LatexUtil) {

	$scope.init = function() {

        $scope.projectsManagementBoxBlockUI = blockUI.instances.get('projectsManagementBox');
        $scope.documentsManagementBoxBlockUI = blockUI.instances.get('documentsManagementBox');
        $scope.documentPackageManagementBoxBlockUI = blockUI.instances.get('documentPackageManagementBox');
        $scope.collaboratorsManagementBoxBlockUI = blockUI.instances.get('collaboratorsManagementBox');
        $scope.collaborationChartBoxBlockUI = blockUI.instances.get('collaborationChartBox');
        $scope.annotatorBoxBlockUI = blockUI.instances.get('annotatorBoxBlockUI');
        $scope.documentCollaborationsModalBoxBlockUI = blockUI.instances.get('documentCollaborationsModalBox');
        $scope.statisticsModalBoxBlockUI = blockUI.instances.get('statisticsModalBox');
        $scope.documentModalBoxBlockUI = blockUI.instances.get('documentModalBox');
        $scope.commentsModalBoxBlockUI = blockUI.instances.get('commentsModalBox');

        $scope.listProjects();
        $scope.availableDocumentStatus = [{label:'ALL', value:null}, {label:'CHECKED', value:'CHECKED'}, {label:'PRECHECKED', value:'PRECHECKED'}, {label:'UNCHECKED', value:'UNCHECKED'}]
        $scope.availableWordCloudTypes = {
            'TAG':[
                {label:'VALUE', value: 'value'},
                {label:'FROM-CONNECTOR', value:'from-connector'},
                {label:'TO-CONNECTOR', value:'to-connector'}
            ],
            'RELATION':[
                {label:'CONNECTOR', value: 'connector'},
                {label:'FROM-TAG', value:'from-tag'},
                {label:'TO-TAG', value:'to-tag'}
            ]
        };
        $scope.availableWordCloudDimensions = [
            {label:'FORM', value: 'form'},
            {label:'LEMMA', value:'lemma'}
        ];
        $scope.selection = {
            documentsPerPage : 5, paginationSize : 10, currentDocumentsPage : 1,
            documentStatus: $scope.availableDocumentStatus[0], collaborationByCollaboratorEmail: [],
            showGsaStatistics: true
        }
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

	$scope.onChangeSelectedProject = function(){
	    $scope.documentPackageStatistics = null;
        $scope.statisticsMap = null;
        $scope.statisticsSummaryMap = null;
	    $scope.selection.documentPackage = null;
	    $scope.documents = null;
	    $scope.selection.currentDocumentsPage = 1;

        $scope.documentsManagementBoxBlockUI.start();

        ProjectService.getOntologyMap(
            $scope.selection.project.id
        ).then(function(response) {
            $scope.ontologyMap = response.data;
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.documentsManagementBoxBlockUI.stop();
        });
	}

	$scope.onChangeSelectedDocumentStatus = function(){
	    $scope.listDocuments(1);
	}

    $scope.onChangeSelectedDocumentPackage = function(){

        $scope.statisticsMap = null;
        $scope.statisticsSummaryMap = null;

        $scope.loadBasicDocumentPackageStatistics(function(){

            $scope.statisticsCollaboratorsFilter = [];
            $scope.collaboratorsByEmail = [];
            angular.forEach($scope.selection.documentPackage.collaborators, function(collaborator){
                $scope.statisticsCollaboratorsFilter[collaborator.email] = true;
                $scope.collaboratorsByEmail[collaborator.email] = collaborator;
            });

            $scope.listDocuments(1);
        });
	}

	$scope.loadModalDocument = function(documentId){
        $scope.documentModalBoxBlockUI.start();
        DocumentService.get(
            documentId
        ).then(function(response) {
            var config = {
                entities : $scope.selection.project.entities,
                showIndex : false,
                showMetadata : true,
                mode : 'validation',
                readOnly: true,
                maxDocumentHeight: 500
            }
            $timeout(function(){
                AnnotatorJS.render('modalAnnotatorContainer', response.data, config)
            }, 500);
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.documentModalBoxBlockUI.stop();
        });
	}

    $scope.loadDocumentsSummary = function() {

        $scope.documentsSummary = {totalOfDocuments:0, totalOfPages:0, paginationArray:[]}

        if ($scope.selection.documentStatus.value == 'CHECKED'){
            $scope.documentsSummary.total = $scope.documentPackageStatistics.checked;
        }else if ($scope.selection.documentStatus.value == 'PRECHECKED'){
            $scope.documentsSummary.total = $scope.documentPackageStatistics.prechecked;
        }else if ($scope.selection.documentStatus.value == 'UNCHECKED'){
            $scope.documentsSummary.total = $scope.documentPackageStatistics.unchecked;
        }else{
            $scope.documentsSummary.total = $scope.documentPackageStatistics.checked + $scope.documentPackageStatistics.prechecked + $scope.documentPackageStatistics.unchecked;
        }

        $scope.documentsSummary.totalOfPages = Math.ceil(parseInt($scope.documentsSummary.total)/$scope.selection.documentsPerPage)

        if($scope.documentsSummary.totalOfPages){
            var startPage = $scope.selection.currentDocumentsPage ? $scope.selection.currentDocumentsPage : 1;

            if($scope.selection.currentDocumentsPage + $scope.selection.paginationSize > $scope.documentsSummary.totalOfPages){
                startPage = $scope.documentsSummary.totalOfPages - $scope.selection.paginationSize + 1;
                startPage = startPage > 0 ? startPage : 1;
            }

            for(var i=0; i < $scope.selection.paginationSize; i++){
                if(startPage+i > $scope.documentsSummary.totalOfPages){
                    break;
                }
                $scope.documentsSummary.paginationArray.push(startPage+i);
            }
        }else{
            $scope.documentsSummary.totalOfPages = 1;
        }

    }

	$scope.loadBasicDocumentPackageStatistics = function(successCallback) {
	    $scope.documentsManagementBoxBlockUI.start();

	    DocumentPackageService.getStatistics(
            $scope.selection.documentPackage.id
        ).then(function(response) {
            $scope.documentPackageStatistics = response.data;
            if(successCallback){
                successCallback();
            }
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
            console.info(response);
        }).finally(function(){
            $scope.documentsManagementBoxBlockUI.stop();
        });
	}

    $scope.listDocuments = function(page) {

        $scope.subjectDocument = null;

        $scope.documentsManagementBoxBlockUI.start();

        if(!page){
            page = 1;
        }

        $scope.selection.currentDocumentsPage = page;

        DocumentService.list(
            $scope.selection.project.id,
            $scope.selection.documentPackage.id,
            (page-1)*$scope.selection.documentsPerPage,
            $scope.selection.documentsPerPage,
            $scope.selection.documentStatus.value,
            false, true
        ).then(function(response) {
		    $scope.documents = response.data;
		    $scope.loadDocumentsSummary();
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.documentsManagementBoxBlockUI.stop();
        });
    }

    $scope.onShowCreateDocumentPackageModal = function(){
        $scope.documentPackage = {
            projectId: $scope.selection.project.id,
            randomAnnotation: true,
            usePrecheckAgreementThreshold: false,
            precheckAgreementThreshold: 1,
            useTagAgreement: true,
            useRelationAgreement: true,
            useConnectorAgreement: true
        }
        $scope.isInEditMode = false;
    }

    $scope.onShowUpdateDocumentPackageModal = function(){
        $scope.documentPackage = angular.copy($scope.selection.documentPackage);
        $scope.isInEditMode = true;
    }

    $scope.onShowCollaboratorsModal = function(){
        $scope.collaborator = {}
        $scope.group = {}
    }

    $scope.onShowAddDocumentModal = function(){
        $scope.document = {};
        $scope.metadataList = [];
        $scope.isInEditMode = false;
    }

    $scope.loadSubjectDocumentModes = function(){
        $scope.subjectDocumentModes = [{label:'Validation', value:'validation', doc:$scope.subjectDocument}];

        if(!$scope.selection.subjectDocumentMode){
            $scope.selection.subjectDocumentMode = $scope.subjectDocumentModes[0];
        }
        angular.forEach($scope.subjectDocument.collaborations, function(collaboration){
            //var label = collaboration.collaborator.firstName +' '+collaboration.collaborator.lastName;
            var label = collaboration.collaborator.email;

            var doc = {
                name: $scope.subjectDocument.name,
                metadata: angular.copy($scope.subjectDocument.metadata),
                sentences: angular.copy($scope.subjectDocument.sentences),
                tags: collaboration.tags,
                relations: collaboration.relations,
                logs: collaboration.logs,
                comments: collaboration.comments
            };

            $scope.subjectDocumentModes.push({label:label, value:'view', doc:doc});

            if(collaboration.reannotation){
                var reannotation = {
                    name: $scope.subjectDocument.name,
                    metadata: angular.copy($scope.subjectDocument.metadata),
                    sentences: angular.copy($scope.subjectDocument.sentences),
                    tags: collaboration.reannotation.tags,
                    relations: collaboration.reannotation.relations,
                    logs: collaboration.reannotation.logs,
                    comments: collaboration.reannotation.comments
                };

                $scope.subjectDocumentModes.push({label:label+':reannotation', value:'view', doc:reannotation});
            }

        });
    }

    $scope.showSubjectDocument = function(document){
        $scope.subjectDocument = document;
        $scope.selection.subjectDocumentMode = null;
        $scope.reloadSubjectDocument(function(){
            $scope.loadSubjectDocumentModes();
            $scope.loadSubjectDocumentAnnotator();
        });
    }

    $scope.onChangeSubjectDocumentMode = function(){
        $scope.subjectDocument = $scope.selection.subjectDocumentMode.doc;
        $scope.loadSubjectDocumentAnnotator();
    }

    $scope.reloadSubjectDocument = function(callback){
        DocumentService.get(
            $scope.subjectDocument.id
        ).then(function(response) {
            $scope.subjectDocument = response.data;
            callback();
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.annotatorBoxBlockUI.stop();
        });
    }

    $scope.loadSubjectDocumentAnnotator = function(){

        console.info($scope.subjectDocument);

        var config = {
            entities : $scope.selection.project.entities,
            onChange : function(doc, changeLog, undoCallback){

                if($scope.selection.subjectDocumentMode.value == 'validation'){
                    $scope.annotatorBoxBlockUI.start();
                    console.info(doc.stateKey);
                    DocumentService.update(doc, changeLog).then(function(response) {
                        $scope.loadBasicDocumentPackageStatistics();
                        doc.stateKey = response.data;
                    }, function(response) {
                        console.info(response);
                        undoCallback();
                        PNotifyUtil.showError(':(', 'Something unexpected happened');
                    }).finally(function(){
                        $scope.annotatorBoxBlockUI.stop();
                    });
                }
            },
            showIndex : false,
            showMetadata : true,
            mode : $scope.selection.subjectDocumentMode.value
        }

        $scope.goToAnnotatorBox();

        $timeout(function(){
            AnnotatorJS.render("annotatorContainer", $scope.subjectDocument, config)
        }, 500);

    }

    $scope.hideSubjectDocument = function(){
        delete $scope.subjectDocument;
    }

    $scope.onShowUpdateDocumentModal = function(document){
        $scope.selection.document = document;
        $scope.document = angular.copy(document);
        $scope.metadataList = [];

        angular.forEach(Object.keys(document.metadata), function(key){
            $scope.metadataList.push({key:key, value:document.metadata[key]});
        });

        $scope.isInEditMode = true;
    }

    $scope.addMetadata = function() {
	    $scope.metadataList.push({key:'', value:''});
	}

	$scope.removeMetadata = function(metadata) {
	    ArrayUtil.remove($scope.metadataList, metadata);
	}

    $scope.saveDocumentPackage = function(){

        var canSave = true;

        /*if($scope.documentPackageStatistics){
            var total = $scope.documentPackageStatistics.checked + $scope.documentPackageStatistics.unchecked;

            if($scope.documentPackage.warmUpSize > total){
                PNotifyUtil.showError(':(', 'Invalid warm up size');
                canSave = false;
            }
            if($scope.documentPackage.reannotationStep > total){
                PNotifyUtil.showError(':(', 'Invalid reannotation step');
                canSave = false;
            }
        }*/

        if(canSave){

            $scope.documentPackageManagementBoxBlockUI.start();

            var action = !$scope.isInEditMode ? DocumentPackageService.insert : DocumentPackageService.update;

            action($scope.documentPackage).then(function(response) {
                if(!$scope.isInEditMode){
                    $scope.documentPackage.id = response.data;
                    $scope.selection.project.documentPackages.push($scope.documentPackage);
                    $scope.selection.documentPackage = $scope.documentPackage;
                    $scope.selection.documentPackage.collaborators = [];
                    $scope.selection.documentPackage.groups = [{id: 0, name: 'DEFAULT', warmUpSize: 0, reannotationStep: 0}];
                    $scope.documents = null;
                    PNotifyUtil.showSuccess(':)', 'Documents package added');
                }else{
                    $scope.selection.documentPackage.name = $scope.documentPackage.name;
                    $scope.selection.documentPackage.randomAnnotation = $scope.documentPackage.randomAnnotation;
                    $scope.selection.documentPackage.showSelfAgreementFeedback = $scope.documentPackage.showSelfAgreementFeedback;
                    $scope.selection.documentPackage.selfAgreementFeedbackGoal = $scope.documentPackage.selfAgreementFeedbackGoal;
                    $scope.selection.documentPackage.usePrecheckAgreementThreshold = $scope.documentPackage.usePrecheckAgreementThreshold;
                    $scope.selection.documentPackage.precheckAgreementThreshold = $scope.documentPackage.precheckAgreementThreshold;
                    PNotifyUtil.showSuccess(':)', 'Documents package updated');
                }
                $scope.loadBasicDocumentPackageStatistics();
            }, function(response) {
                PNotifyUtil.showError(':(', 'Something unexpected happened');
                console.info(response);
            }).finally(function(){
                $scope.documentPackageManagementBoxBlockUI.stop();
            });
        }
    }

    $scope.removeDocumentPackage = function(){
        $scope.documentPackageManagementBoxBlockUI.start();
		DocumentPackageService.remove($scope.selection.documentPackage.id).then(function(response) {
		    ArrayUtil.remove($scope.selection.project.documentPackages, $scope.selection.documentPackage);
		    $scope.selection.documentPackage = null;
		    $scope.documents = null;
		    PNotifyUtil.showSuccess(':)', 'Documents package removed');
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.documentPackageManagementBoxBlockUI.stop();
        });
    }

    $scope.insertGroup = function() {
        $scope.collaboratorsManagementBoxBlockUI.start();
        DocumentPackageService.insertGroup(
            $scope.selection.documentPackage.id,
            $scope.group
        ).then(function(response) {
            $scope.group.id = parseInt(response.data);
            $scope.selection.documentPackage.groups.push($scope.group);
            PNotifyUtil.showSuccess(':)', 'Group added');
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
		    $scope.group = {}
            $scope.collaboratorsManagementBoxBlockUI.stop();
        });
    }

    $scope.removeGroup = function(group) {
        $scope.collaboratorsManagementBoxBlockUI.start();
        DocumentPackageService.removeGroup(
            $scope.selection.documentPackage.id,
            group.id
        ).then(function(response) {
            ArrayUtil.remove($scope.selection.documentPackage.groups, group);
            var defaultGroup = $scope.selection.documentPackage.groups.filter(function(v){
                return v.id == 0;
            })[0];

            angular.forEach($scope.selection.documentPackage.collaborators, function(collaborator){
                if(collaborator.group.id == group.id){
                    collaborator.group = defaultGroup;
                }
            });

            PNotifyUtil.showSuccess(':)', 'Group removed');

        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.collaboratorsManagementBoxBlockUI.stop();
        });
    }

    $scope.insertCollaborator = function() {
        $scope.collaboratorsManagementBoxBlockUI.start();
        DocumentPackageService.insertCollaborator(
            $scope.selection.documentPackage.id,
            {email: $scope.collaborator.email, groupId: $scope.collaborator.group.id}
        ).then(function(response) {
            $scope.selection.documentPackage.collaborators.push($scope.collaborator);
            PNotifyUtil.showSuccess(':)', 'Collaborator added');
        }, function(response) {
            if(response.status = 404){
                PNotifyUtil.showError(':(', 'Not registered user');
            }else{
                PNotifyUtil.showError(':(', 'Something unexpected happened');
            }
        	console.info(response);
        }).finally(function(){
		    $scope.collaborator = {};
            $scope.collaboratorsManagementBoxBlockUI.stop();
        });
    }

    $scope.onChangeCollaboratorGroup = function(collaborator){
        $scope.collaboratorsManagementBoxBlockUI.start();
        DocumentPackageService.updateCollaborator(
            $scope.selection.documentPackage.id,
            {email: collaborator.email, groupId: collaborator.group.id}
        ).then(function(response) {
            PNotifyUtil.showSuccess(':)', 'Collaborator updated');
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.collaboratorsManagementBoxBlockUI.stop();
        });
    }

    $scope.removeCollaborator = function(collaborator) {
        $scope.collaboratorsManagementBoxBlockUI.start();
        DocumentPackageService.removeCollaborator(
            $scope.selection.documentPackage.id,
            collaborator.email
        ).then(function(response) {
            ArrayUtil.remove($scope.selection.documentPackage.collaborators, collaborator);
            PNotifyUtil.showSuccess(':)', 'Collaborator removed');
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.collaboratorsManagementBoxBlockUI.stop();
        });
    }

    $scope.changeCollaborationsStatus = function(collaborator, newStatus) {
	    $scope.collaboratorsManagementBoxBlockUI.start();
	    DocumentPackageService.changeCollaborationsStatus(
            $scope.selection.documentPackage.id,
            collaborator.email,
            newStatus
        ).then(function(response) {
            PNotifyUtil.showSuccess(':)', 'Status changed');
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
            console.info(response);
        }).finally(function(){
            $scope.collaboratorsManagementBoxBlockUI.stop();
        });
	}

    $scope.saveDocument = function(refreshMetadata) {

        $scope.documentsManagementBoxBlockUI.start();

        var action = $scope.isInEditMode
            ? function(document){return DocumentService.update(document)}
            : function(document){return DocumentService.insert($scope.selection.documentPackage.id, document)};

        if(refreshMetadata){
            $scope.document.metadata = {}
            angular.forEach($scope.metadataList, function(m){
                if(m.key){
                    $scope.document.metadata[m.key] = m.value;
                }
            });
        }

        action($scope.document).then(function(response) {

            $scope.listDocuments($scope.selection.currentDocumentsPage);
            $scope.loadBasicDocumentPackageStatistics();

            if($scope.isInEditMode){
                PNotifyUtil.showSuccess(':)', 'Document updated');
            }else{
                PNotifyUtil.showSuccess(':)', 'Document added');
            }
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.documentsManagementBoxBlockUI.stop();
        });
    }

    $scope.updateDocumentStatus = function(document, status){

        $scope.documentsManagementBoxBlockUI.start();

        $scope.document = document;

        DocumentService.get(
            $scope.document.id
        ).then(function(response) {
            if(response.data.status != status){

                $scope.documentsManagementBoxBlockUI.start();

                $scope.document = response.data;

                var changeLog = {
                    action : 'CHANGE',
                    subject : {
                        type: 'STATUS',
                        value: {
                            old : $scope.document['status'],
                            new : status
                        }
                    },
                    firedBy : 'DEFAULT'
                }
                DocumentService.update($scope.document, changeLog).then(function(response) {
                    $scope.listDocuments($scope.selection.currentDocumentsPage);
                    $scope.loadBasicDocumentPackageStatistics();
                    $scope.document.status = status;
                    $scope.document.stateKey = response.data;
                    console.info($scope.document.stateKey);
                }, function(response) {
                    console.info(response);
                    PNotifyUtil.showError(':(', 'Something unexpected happened');
                }).finally(function(){
                    $scope.documentsManagementBoxBlockUI.stop();
                });
            }
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.documentsManagementBoxBlockUI.stop();
        });

    }

    $scope.removeDocument = function(document) {
	    $scope.documentsManagementBoxBlockUI.start();
        DocumentService.remove(
            document.id
        ).then(function(response) {
            $scope.listDocuments($scope.selection.currentDocumentsPage);
            PNotifyUtil.showSuccess(':)', 'Document removed');
            $scope.loadBasicDocumentPackageStatistics();
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.documentsManagementBoxBlockUI.stop();
        });
    }

    $scope.exportDocument = function(document){
        $scope.exportDetails = {
            document: document,
            includeMetadata: true,
            includeText: true,
            includeCollaboration: true,
            includeStatus: true,
            includeDescription: true,
            includeLog: true,
            includeComments: true
        }
    }

    $scope.exportDocumentPackage = function(){
        $scope.exportDetails = {
            includeUnchecked: true,
            includePrechecked: true,
            includeChecked: true,
            includeMetadata: true,
            includeText: true,
            includeCollaboration: true,
            includeStatus: true,
            includeDescription: true,
            includeLog: true,
            includeComments: true
        }
	}

    $scope.export = function(){
        if($scope.exportDetails.document){
            $scope.documentsManagementBoxBlockUI.start();
            DocumentService.get(
                $scope.exportDetails.document.id, true,
                $scope.exportDetails.includeMetadata,
                $scope.exportDetails.includeText,
                $scope.exportDetails.includeCollaboration,
                $scope.exportDetails.includeStatus,
                $scope.exportDetails.includeDescription,
                $scope.exportDetails.includeLog,
                $scope.exportDetails.includeComments
            ).then(function(response) {
                var blob = new Blob([response.data], {type: 'text/plain'});
                saveAs(blob, document.name);
            }, function(response) {
                PNotifyUtil.showError(':(', 'Something unexpected happened');
                console.info(response);
            }).finally(function(){
                $scope.documentsManagementBoxBlockUI.stop();
            });
        }else{
            $scope.documentsManagementBoxBlockUI.start();
            DocumentPackageService.getDocumentsZip(
                $scope.selection.documentPackage.id,
                $scope.exportDetails.includeUnchecked,
                $scope.exportDetails.includePrechecked,
                $scope.exportDetails.includeChecked,
                $scope.exportDetails.includeMetadata,
                $scope.exportDetails.includeText,
                $scope.exportDetails.includeCollaboration,
                $scope.exportDetails.includeStatus,
                $scope.exportDetails.includeDescription,
                $scope.exportDetails.includeLog,
                $scope.exportDetails.includeComments
            ).then(function(response) {
                var blob = new Blob([response.data], {type: 'application/zip, application/octet-stream'});
                saveAs(blob, $scope.selection.documentPackage.name+'.zip');
            }, function(response) {
                PNotifyUtil.showError(':(', 'Something unexpected happened');
            }).finally(function(){
                $scope.documentsManagementBoxBlockUI.stop();
            });
        }
	}

	$scope.importDocuments = function(){

        $scope.documentsManagementBoxBlockUI.start();

	    try {

	        var submittedDocs = 0;
            var successfulDocs = 0;
            var unsuccessfulCount = 0;

	        angular.forEach($scope.documentsFiles, function(documentsFile){
                DocumentService.insert($scope.selection.documentPackage.id,
                    {
                        name: documentsFile.name,
                        text: Base64Util.base64ToString(documentsFile.data.split(',')[1]),
                        isPlainText: $scope.importedDocumentsIsPlainText
                    }
                ).then(function(response) {
                    successfulDocs++;
                    PNotifyUtil.showSuccess(':)', 'Document '+ documentsFile.name +' has imported');
                }, function(response) {
                    unsuccessfulCount++;
                    PNotifyUtil.showError(':(', 'Document '+ documentsFile.name +' has not imported');
                }).finally(function(){
                    submittedDocs++;
                    if(submittedDocs == $scope.documentsFiles.length){
                        $scope.listDocuments($scope.selection.currentDocumentsPage);

                        if(submittedDocs == successfulDocs){
                            PNotifyUtil.showSuccess(':)', 'Documents imported');
                        }else{
                            PNotifyUtil.showWarning(':|', unsuccessfulCount+' of '+submittedDocs+' could not be added');
                        }

                        $scope.documentsManagementBoxBlockUI.stop();
                    }
                    $scope.loadBasicDocumentPackageStatistics();
                });
            });

        } catch(e) {
            $scope.documentsManagementBoxBlockUI.stop();
            PNotifyUtil.showError(':(', 'Invalid input file');
            console.info(e);
        }
	}

	$scope.goToAnnotatorBox = function(){
	    $document.scrollTo(angular.element('#annotatorBox'), 70, 1000);
	}

	$scope.loadCollaborationByCollaboratorEmail = function(document){
	    $scope.selection.collaborationByCollaboratorEmail = [];
	    for (var i = 0; i < document.collaborations.length; i++) {
            var collaboration = document.collaborations[i];
            $scope.selection.collaborationByCollaboratorEmail[collaboration.collaborator.email] = collaboration;
        }
	}

	$scope.onShowDocumentCollaborationsModal = function(document){
        $scope.selection.document = document;
        $scope.loadCollaborationByCollaboratorEmail(document);
    }

	$scope.updateCollaborationStatus = function(document, collaborator, status) {
	    $scope.documentCollaborationsModalBoxBlockUI.start();
	    DocumentService.updateCollaborationStatus(
            document.id, collaborator.email, status
        ).then(function(response) {
            $scope.selection.collaborationByCollaboratorEmail[collaborator.email].status = status;
        }, function(response) {
            console.info(response);
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.documentCollaborationsModalBoxBlockUI.stop();
        });
    }

    $scope.changeDocumentsStatus = function(newStatus) {
	    $scope.documentsManagementBoxBlockUI.start();
	    DocumentPackageService.changeDocumentsStatus(
            $scope.selection.documentPackage.id,
            newStatus
        ).then(function(response) {
            $scope.listDocuments($scope.selection.currentDocumentsPage);
            $scope.loadBasicDocumentPackageStatistics();
            PNotifyUtil.showSuccess(':)', 'Documents status changed');
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
            console.info(response);
        }).finally(function(){
            $scope.documentsManagementBoxBlockUI.stop();
        });
	}

	$scope.removeDocuments = function() {
	    $scope.documentsManagementBoxBlockUI.start();
	    DocumentPackageService.removeDocuments(
            $scope.selection.documentPackage.id
        ).then(function(response) {
            $scope.listDocuments($scope.selection.currentDocumentsPage);
            $scope.loadBasicDocumentPackageStatistics();
            PNotifyUtil.showSuccess(':)', 'Documents removed');
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
            console.info(response);
        }).finally(function(){
            $scope.documentsManagementBoxBlockUI.stop();
        });
	}

    $scope.init();

	//STATISTICS

    $scope.getStatisticsCollaboratorsToFilter = function() {
        var collaboratorsToFilter = [];
        angular.forEach($scope.selection.documentPackage.collaborators, function(collaborator){
            if($scope.statisticsCollaboratorsFilter[collaborator.email]){
                collaboratorsToFilter.push(collaborator.email);
            }
        });
        return collaboratorsToFilter;
    };

    $scope.filterStatisticsModal = function() {
        $scope.statisticsMap = null;
        $scope.statisticsFilterSelected = null;
        $scope.loadStatistics($scope.selection.selectedStatisticsType, $scope.selection.selectedStatisticsFilter);
    };

    $scope.onShowStatisticsModal = function() {
        //$scope.statisticsFilterSelected = {};
        //$scope.loadStatistics('token', 'all');
        //$scope.loadStatistics('status', 'all');

        if(!$scope.selection.selectedStatisticsType || !$scope.selection.selectedStatisticsFilter){
            $scope.loadStatistics('status', 'all');
        }else{
            $scope.loadStatistics($scope.selection.selectedStatisticsType, $scope.selection.selectedStatisticsFilter);
        }
    };

    $scope.loadStatistics = function(type, filter, successCallback) {

        $scope.selection.selectedStatisticsType = type;
        $scope.selection.selectedStatisticsFilter = filter;

        if(!$scope.statisticsMap){
            $scope.statisticsMap = {}
        }
        if(!$scope.statisticsFilterSelected){
            $scope.statisticsFilterSelected = {}
        }

        $timeout(function() {
            window.dispatchEvent(new Event('resize')); // resize issues workaround
        },500);

        $scope.statisticsFilterSelected[type] = filter;

        if(!$scope.statisticsMap[type] || !$scope.statisticsMap[type][filter]){

            $scope.statisticsModalBoxBlockUI.start();

            DocumentPackageService.getStatistics(
                $scope.selection.documentPackage.id, null, type,
                'words' != type ? true : false,
                'words' != type ? $scope.getStatisticsCollaboratorsToFilter() : null,
                filter
            ).then(function(response) {

                if(!$scope.statisticsMap[type]){
                    $scope.statisticsMap[type] = [];
                }

                var result = response.data;
                var GSA_LABEL = '(GSA)';
                var series = [];

                $scope.statisticsMap[type][filter] = result;

                console.log(result);

                if(result.collaborations && result.collaborations.sort){
                    result.collaborations = result.collaborations.sort(function(a, b){
                        var collaboratorA = $scope.collaboratorsByEmail[a.collaborator];
                        var labelA = a.collaborator;
                        if(collaboratorA){
                            labelA = collaboratorA.lastName+', '+collaboratorA.firstName;
                        }

                        var collaboratorB = $scope.collaboratorsByEmail[b.collaborator];
                        var labelB = b.collaborator;

                        if(collaboratorB){
                            labelB = collaboratorB.lastName+', '+collaboratorB.firstName;
                        }

                        return labelA.localeCompare(labelB);
                    });
                }

                switch (type) {
                    case 'words':

                        $scope.selection.availableWordCloudTags = Object.keys(result.all.tags).sort();
                        $scope.selection.availableWordCloudTags.unshift('ALL');
                        $scope.selection.wordCloudTag = $scope.selection.availableWordCloudTags[0];
                        $scope.selection.wordCloudTagType = 'value';
                        $scope.selection.wordCloudTagDimension = 'form';

                        $scope.selection.availableWordCloudRelations = Object.keys(result.all.relations).sort();
                        $scope.selection.availableWordCloudRelations.unshift('ALL');
                        $scope.selection.wordCloudRelation = $scope.selection.availableWordCloudRelations[0];
                        $scope.selection.wordCloudRelationType = 'connector';
                        $scope.selection.wordCloudRelationDimension = 'form';

                        $scope.onChangeWordcloudParameter('TAG');
                        $scope.onChangeWordcloudParameter('RELATION');

                        break;
                    case 'status':

                        if($scope.selection.showGsaStatistics) {
                            $scope.fillBarSeries(series, {'(Unchecked)': result.unchecked}, GSA_LABEL, '#ff7f0e');
                            $scope.fillBarSeries(series, {'(Checked)': result.checked}, GSA_LABEL, '#1f77b4');
                            $scope.fillBarSeries(series, {'(Prechecked)': result.prechecked}, GSA_LABEL, '#b7d9f1');
                        }

                        angular.forEach(result.collaborations, function(collaboration){
                            var collaborator = $scope.collaboratorsByEmail[collaboration.collaborator];
                            var collaboratorLabel = collaborator.lastName+', '+collaborator.firstName;

                            $scope.fillBarSeries(series, {'Undone': collaboration.undone}, collaboratorLabel, '#d81d08');
                            $scope.fillBarSeries(series, {'Done': collaboration.done}, collaboratorLabel, '#2ca02c');
                        });

                        $scope.plotBarSeries('statusChart', series, 200, true, true, 'number of documents', '');

                        break;
                    case 'tag':
                    case 'relation':
                    case 'connector':

                        console.log(result);

                        if($scope.selection.showGsaStatistics) {
                            angular.forEach(result.values, function (value) {
                                var data = {};
                                data[value.label] = value.count;
                                $scope.fillBarSeries(series, data, GSA_LABEL);
                            });
                        }

                        angular.forEach(result.collaborations, function(collaboration){

                            var collaborator = $scope.collaboratorsByEmail[collaboration.collaborator];
                            var collaboratorLabel = collaborator.lastName+', '+collaborator.firstName;

                            var data = {};
                            data[collaboration.label] = collaboration.count;
                            $scope.fillBarSeries(series, data, collaboratorLabel);
                        });

                        $scope.plotBarSeries(type + 'Chart', series, 200, true, true, 'number of '+type+'s', '');

                        var frequencySeries = {x:[], y:[]};
                        angular.forEach(Object.keys(result.frequency).sort(), function(count){
                            frequencySeries.x.push(count);
                            frequencySeries.y.push(result.frequency[count]);
                        });

                        $scope.plotBarSeries(type + 'FrequencyChart', {'frequency': frequencySeries}, null, false, false , 'number of '+type+'s', 'number of documents');

                        break;
                    case 'token':

                        if($scope.selection.showGsaStatistics) {
                            $scope.fillBarSeries(series, {'Tag': result.values.tag}, GSA_LABEL);
                            $scope.fillBarSeries(series, {'Empty': result.values.empty}, GSA_LABEL);
                            $scope.fillBarSeries(series, {'Connector': result.values.connector}, GSA_LABEL);
                        }

                        angular.forEach(result.collaborations, function(collaboration){
                            var collaborator = $scope.collaboratorsByEmail[collaboration.collaborator];
                            var collaboratorLabel = collaborator.lastName+', '+collaborator.firstName;

                            $scope.fillBarSeries(series, {'Tag': collaboration.tag}, collaboratorLabel);
                            $scope.fillBarSeries(series, {'Empty': collaboration.empty}, collaboratorLabel);
                            $scope.fillBarSeries(series, {'Connector': collaboration.connector}, collaboratorLabel);
                        });

                        $scope.plotBarSeries('coverageChart', series, 200, true, true, 'number of tokens', '');

                        var frequencySeries = {x:[], y:[]};
                        angular.forEach(Object.keys(result.frequency).sort(), function(count){
                            frequencySeries.x.push(count);
                            frequencySeries.y.push(result.frequency[count]);
                        });

                        $scope.plotBarSeries('tokenFrequencyChart', {'frequency': frequencySeries}, null, false, false, 'number of tokens', 'number of documents');

                        break;
                    case 'summary':

                        console.log(result);

                        var statisticsTimeSpentSummary = [];
                        var statisticsSummaryByCollaborator = [];

                        $scope.statisticsSummary = [];
                        $scope.statisticsSummaryMap = [];

                        angular.forEach(result, function(data){

                            var summary = {
                                id: data.id,
                                name: data.name,
                                numberOfTokens: data.numberOfTokens,
                                timeSpent: data.collaborationsSummary.timeSpentSum,
                                timeSpentAvg: data.collaborationsSummary.timeSpentMean,
                                timeSpentSd: data.collaborationsSummary.timeSpentStandardDeviation,
                                numberOfViews: data.collaborationsSummary.numberOfViewsSum,
                                numberOfViewsAvg: data.collaborationsSummary.numberOfViewsMean,
                                numberOfViewsSd: data.collaborationsSummary.numberOfViewsStandardDeviation/*,
                                elapsedTime:  new Date(1970, 0, 1).setSeconds(parseInt(data.collaborationsSummary.timeSpentSum)),
                                elapsedTimeAvg: new Date(1970, 0, 1).setSeconds(parseInt(data.collaborationsSummary.timeSpentMean)),
                                elapsedTimeSd: new Date(1970, 0, 1).setSeconds(parseInt(data.collaborationsSummary.timeSpentStandardDeviation))*/
                            };

                            var elapsedTime = new Date(1970, 0, 1);
                            elapsedTime.setSeconds(summary.timeSpent);
                            summary.elapsedTime = DateUtil.get_difference_as_string(new Date(1970, 0, 1), elapsedTime);

                            elapsedTime = new Date(1970, 0, 1);
                            elapsedTime.setSeconds(summary.timeSpentAvg);
                            summary.elapsedTimeAvg = DateUtil.get_difference_as_string(new Date(1970, 0, 1), elapsedTime);

                            elapsedTime = new Date(1970, 0, 1);
                            elapsedTime.setSeconds(summary.timeSpentSd);
                            summary.elapsedTimeSd = DateUtil.get_difference_as_string(new Date(1970, 0, 1), elapsedTime);

                            $scope.statisticsSummary.push(summary);

                            $scope.statisticsSummaryMap[data.id] = [];

                            angular.forEach(Object.keys(data.collaborations), function(collaborator){
                                $scope.statisticsSummaryMap[data.id][collaborator] = data.collaborations[collaborator];
                                $scope.statisticsSummaryMap[data.id][collaborator].id = data.id;
                                $scope.statisticsSummaryMap[data.id][collaborator].name = data.name;
                                $scope.statisticsSummaryMap[data.id][collaborator].numberOfTokens = data.numberOfTokens;

                                /*if(!statisticsTimeSpentSummary[collaborator]){
                                    statisticsTimeSpentSummary[collaborator] = [data.collaborations[collaborator].timeSpent];
                                }else{
                                    statisticsTimeSpentSummary[collaborator].push(data.collaborations[collaborator].timeSpent);
                                }*/
                                if(!statisticsSummaryByCollaborator[collaborator]){
                                    statisticsSummaryByCollaborator[collaborator] = {
                                        timeSpent: [data.collaborations[collaborator].timeSpent],
                                        numberOfViews: [data.collaborations[collaborator].numberOfViews]
                                    }
                                }else{
                                    statisticsSummaryByCollaborator[collaborator].timeSpent.push(data.collaborations[collaborator].timeSpent);
                                    statisticsSummaryByCollaborator[collaborator].numberOfViews.push(data.collaborations[collaborator].numberOfViews);
                                }

                            });

                            //$scope.statisticsTimeSpentSummary = [];
                            $scope.collaboratorStatisticsSummary = [];
                            angular.forEach(Object.keys(statisticsSummaryByCollaborator), function(collaboratorEmail){
                                var collaborator = $scope.collaboratorsByEmail[collaboratorEmail];
                                if(collaborator){
                                    /*var collaboratorLabel = collaborator.lastName + ', ' + collaborator.firstName;
                                    var elapsedTime = angular.copy($scope.elapsedBeginDate);
                                    elapsedTime.setSeconds(statisticsTimeSpentSummary[collaboratorEmail]);
                                    console.log(elapsedTime);*/

                                    var collaboratorSummary = statisticsSummaryByCollaborator[collaboratorEmail];

                                    var summary = {
                                        collaborator: collaborator.lastName + ', ' + collaborator.firstName,
                                        timeSpent: StatisticsUtil.sum(collaboratorSummary.timeSpent),
                                        timeSpentAvg: parseInt(StatisticsUtil.average(collaboratorSummary.timeSpent)),
                                        timeSpentSd: parseInt(StatisticsUtil.standardDeviation(collaboratorSummary.timeSpent)),
                                        numberOfViews: StatisticsUtil.sum(collaboratorSummary.numberOfViews),
                                        numberOfViewsAvg: StatisticsUtil.average(collaboratorSummary.numberOfViews),
                                        numberOfViewsSd: StatisticsUtil.standardDeviation(collaboratorSummary.numberOfViews)
                                    };
                                    var elapsedTime = new Date(1970, 0, 1);
                                    elapsedTime.setSeconds(summary.timeSpent);
                                    summary.elapsedTime = DateUtil.get_difference_as_string(new Date(1970, 0, 1), elapsedTime);

                                    elapsedTime = new Date(1970, 0, 1)
                                    elapsedTime.setSeconds(summary.timeSpentAvg);
                                    summary.elapsedTimeAvg = DateUtil.get_difference_as_string(new Date(1970, 0, 1), elapsedTime);

                                    elapsedTime = new Date(1970, 0, 1)
                                    elapsedTime.setSeconds(summary.timeSpentSd);
                                    summary.elapsedTimeSd = DateUtil.get_difference_as_string(new Date(1970, 0, 1), elapsedTime);

                                    $scope.collaboratorStatisticsSummary.push(summary);
                                }
                            });

                            $scope.collaboratorStatisticsSummary = $scope.collaboratorStatisticsSummary.sort(function (a, b) {
                                return a.timeSpent-b.timeSpent;
                            });

                        });

                        $scope.statisticsSummarySortName = 'name';
                        $scope.statisticsSummarySortReverse = true;

                        break;
                    case 'agreement':

                        $scope.hasGsaAgreement = false;

                        var buildAgreementChart = function() {

                            var nameByEmail = [];
                            var collaboratorEmails = [];

                            Object.keys(result['all'].agreement).forEach(function (agreementKey) {
                                collaboratorEmails.push(agreementKey.split(':')[0]);
                                collaboratorEmails.push(agreementKey.split(':')[1]);
                            });

                            collaboratorEmails = Array.from(new Set(collaboratorEmails));

                            /*var collaboratorEmails = Array.from(new Set(Object.keys(result['all'].agreement).map(function (agreementKey) {
                                return agreementKey.split(':')[0];
                            })));*/

                            if (!$scope.selection.showGsaStatistics){
                                ArrayUtil.remove(collaboratorEmails, '(GSA)');
                            }

                            $scope.hasGsaAgreement = collaboratorEmails.indexOf('(GSA)') != -1;

                            collaboratorEmails.forEach(function (email) {
                                var collaborator = $scope.collaboratorsByEmail[email];
                                var collaboratorLabel = email == '(GSA)' ? GSA_LABEL : '';
                                if(collaborator){
                                    collaboratorLabel = collaborator.lastName + ', ' + collaborator.firstName;
                                }
                                nameByEmail[email] = collaboratorLabel;
                            });

                            collaboratorEmails = collaboratorEmails.sort(function (email1, email2) {
                                /*var collaborator1 = $scope.collaboratorsByEmail[email1];
                                var collaboratorLabel1 = email1 == '(GSA)' ? GSA_LABEL : '';
                                if(collaborator1){
                                    collaboratorLabel1 = collaborator1.lastName + ', ' + collaborator1.firstName;
                                }
                                nameByEmail[email1] = collaboratorLabel1;

                                var collaborator2 = $scope.collaboratorsByEmail[email2];
                                var collaboratorLabel2 = email2 == '(GSA)' ? GSA_LABEL : '';
                                if(collaborator2){
                                    collaboratorLabel2 = collaborator2.lastName + ', ' + collaborator2.firstName;
                                }
                                nameByEmail[email2] = collaboratorLabel2;*/

                                return nameByEmail[email1].localeCompare(nameByEmail[email2]);
                            });

                            var agreementData = {x: [], y: [], z: []};

                            angular.forEach(Object.keys(result['all'].agreement), function (agreementKey) {
                                var agreement = result['all'].agreement[agreementKey];

                                var agreementKeySplit = agreementKey.split(':');
                                var index1 = collaboratorEmails.indexOf(agreementKeySplit[0]);
                                var index2 = collaboratorEmails.indexOf(agreementKeySplit[1]);

                                var isGsa = agreementKeySplit[0] == '(GSA)' || agreementKeySplit[1] == '(GSA)';

                                if ((isGsa && $scope.selection.showGsaStatistics) || !isGsa){
                                    if (!agreementData.z[index1]) {
                                        agreementData.z[index1] = [];
                                    }
                                    if (!agreementData.z[index2]) {
                                        agreementData.z[index2] = [];
                                    }

                                    agreementData.z[index1][index2] = agreement.cohenKappa.k.toFixed(2);
                                    agreementData.z[index2][index1] = agreement.cohenKappa.k.toFixed(2);
                                }
                            });

                            collaboratorEmails = collaboratorEmails.map(function (collaboratorEmail) {
                                return nameByEmail[collaboratorEmail];
                            });

                            agreementData.x = collaboratorEmails;
                            agreementData.y = collaboratorEmails;

                            $scope.plotHeatMap('agreementChart_' + filter, agreementData);


                            var gsaAgreementOverTimeData = [];
                            var selfAgreementOverTimeData = [];

                            angular.forEach(Object.keys(result), function (docId) {
                                if(docId != 'all'){
                                    angular.forEach(Object.keys(result[docId].agreement), function (agreementKey) {

                                        var agreementKeySplit = agreementKey.split(':');

                                        var isGsa = agreementKeySplit[0] == '(GSA)' || agreementKeySplit[1] == '(GSA)';

                                        //if((isGsa && $scope.selection.showGsaStatistics) || !isGsa) {
                                        if (isGsa || agreementKeySplit[0] == agreementKeySplit[1]) {//GSA agreement or self-agreement

                                            var collaboratorEmail = agreementKeySplit[0] != '(GSA)' ? agreementKeySplit[0] : agreementKeySplit[1];

                                            var collaborationSummary = $scope.statisticsSummaryMap[docId][collaboratorEmail];

                                            var series = isGsa ? gsaAgreementOverTimeData : selfAgreementOverTimeData;

                                            series.push({
                                                docId: docId,
                                                docName: collaborationSummary.name,
                                                y: result[docId].agreement[agreementKey].cohenKappa.k.toFixed(3),
                                                text: collaborationSummary.name + ' <br> At: ' + DateUtil.format(new Date(collaborationSummary.doneAt * 1000), 'yyyy-MM-dd hh:mm:ss'),
                                                doneAt: collaborationSummary.doneAt,
                                                name: nameByEmail[collaboratorEmail]
                                            });
                                        }
                                        //}
                                    });
                                }
                            });

                            gsaAgreementOverTimeData.sort(function(a, b) {
                                return a.doneAt - b.doneAt;
                            });
                            selfAgreementOverTimeData.sort(function(a, b) {
                                return a.doneAt - b.doneAt;
                            });

                            var gsaAgreementsOverTime = {};
                            var selfAgreementsOverTime = {};

                            var mapAgreementOverTimeDataIndex = [];
                            var getAgreementOverTimeDataIndex = function(key){
                                if(!mapAgreementOverTimeDataIndex[key]){
                                    mapAgreementOverTimeDataIndex[key] = 0;
                                }
                                var index = mapAgreementOverTimeDataIndex[key];
                                mapAgreementOverTimeDataIndex[key] = index + 1;
                                return index;
                            };

                            angular.forEach(gsaAgreementOverTimeData, function(v){
                                var i = getAgreementOverTimeDataIndex(v.name+'gsa_overTime');
                                v.x = i;
                                v.text = v.text + ' ('+(i+1)+'º done)';

                                if(!gsaAgreementsOverTime[i]){
                                    gsaAgreementsOverTime[i] = {name: v.docName, values: []};
                                }
                                gsaAgreementsOverTime[i].values.push(parseFloat(v.y));
                            });
                            angular.forEach(selfAgreementOverTimeData, function(v){
                                var i = getAgreementOverTimeDataIndex(v.name+'self_overTime');
                                v.x = i;
                                v.text = v.text + ' ('+(i+1)+'º done)';

                                if(!selfAgreementsOverTime[i]){
                                    selfAgreementsOverTime[i] = {name: v.docName, values: []};
                                }
                                selfAgreementsOverTime[i].values.push(parseFloat(v.y));
                            });

                            /*var gsaAgreementByDocData = angular.copy(gsaAgreementOverTimeData);
                            var selfAgreementByDocData = angular.copy(selfAgreementOverTimeData);
                            var gsaAgreementsByDoc = {};
                            var selfAgreementsByDoc = {};

                            gsaAgreementByDocData.sort(function(a, b) {
                                return a.docName.localeCompare(b.docName);
                            });
                            selfAgreementByDocData.sort(function(a, b) {
                                return a.docName.localeCompare(b.docName);
                            });

                            angular.forEach(gsaAgreementByDocData, function(v){
                                v.x = getAgreementOverTimeDataIndex(v.name);

                                if(!gsaAgreementsByDoc[v.docId]){
                                    gsaAgreementsByDoc[v.docId] = {name: v.docName, values: []};
                                }
                                gsaAgreementsByDoc[v.docId].values.push(parseFloat(v.y));
                            });
                            angular.forEach(selfAgreementByDocData, function(v){
                                v.x = getAgreementOverTimeDataIndex(v.name);

                                if(!selfAgreementsByDoc[v.docId]){
                                    selfAgreementsByDoc[v.docId] = {name: v.docName, values: []};
                                }
                                selfAgreementsByDoc[v.docId].values.push(parseFloat(v.y));
                            });*/

                            $scope.plotScattedChart('agreementOverTimeChart_' + filter, gsaAgreementOverTimeData, true, 'nth done document', 'agreement');
                            $scope.plotScattedChart('selfAgreementOverTimeChart_' + filter, selfAgreementOverTimeData, true, 'nth done document', 'agreement');

                            //$scope.plotScattedChart('agreementByDocChart_' + filter, gsaAgreementByDocData, false, 'documents', 'agreement');
                            //$scope.plotScattedChart('selfAgreementByDocChart_' + filter, selfAgreementByDocData, false, 'documents', 'agreement');

                            
                            var getStandardDeviationData = function(agreements){
                                
                                var standardDeviationData = [];
                                angular.forEach(Object.keys(agreements), function(docId, index){
                                    standardDeviationData.push({
                                        y: StatisticsUtil.standardDeviation(agreements[docId].values).toFixed(3),
                                        x: index,
                                        text: agreements[docId].name
                                    });
                                });
                                
                                return standardDeviationData;
                            };

                            $scope.plotScattedChart('standardDeviationAgreementOverTimeChart_' + filter, getStandardDeviationData(gsaAgreementsOverTime), false, 'nth done document', 'agreement standard deviation');
                            $scope.plotScattedChart('standardDeviationSelfAgreementOverTimeChart_' + filter, getStandardDeviationData(selfAgreementsOverTime), false, 'nth done document', 'agreement standard deviation');

                            //$scope.plotScattedChart('standardDeviationAgreementByDocChart_' + filter, getStandardDeviationData(gsaAgreementsByDoc), false, 'documents', 'agreement standard deviation');
                            //$scope.plotScattedChart('standardDeviationSelfAgreementByDocChart_' + filter, getStandardDeviationData(selfAgreementsByDoc), false, 'documents', 'agreement standard deviation');

                        };

                        if(!$scope.statisticsSummaryMap){
                            $scope.loadStatistics('summary', 'all', buildAgreementChart);
                        }else{
                            buildAgreementChart();
                        }

                        break;
                    default:
                        break;
                }

                if(successCallback){
                    successCallback();
                }

            }, function(response) {
                PNotifyUtil.showError(':(', 'Something unexpected happened');
                console.info(response);
            }).finally(function(){
                $scope.statisticsModalBoxBlockUI.stop();
            });

        }
    };

    $scope.sortBy = function(column) {
        $scope.statisticsSummarySortReverse = ($scope.statisticsSummarySortName === column) ? !$scope.statisticsSummarySortReverse : false;
        $scope.statisticsSummarySortName = column;
    };

    $scope.plotBarSeries = function(chartId, series, leftMargin, isHorizontal, isStacked, xTitle, yTitle, isXCategory){
        $timeout(function() {
            var tempSeries = series;
            series = [];
            var keys = Object.keys(tempSeries);

            var keys = keys.sort();
            angular.forEach(keys, function (key) {
                var values = tempSeries[key];
                series.push(values);
            });

            var barChartConfig = {
                margin: { t: 15},
                xaxis: {title: xTitle},
                yaxis: {title: yTitle}
            }

            if(isXCategory){
                barChartConfig.xaxis.type = 'category';
            }

            barChartConfig.margin.l = leftMargin; //l: 200

            if(isHorizontal){
                barChartConfig.orientation = 'h';
            }
            if(isStacked){
                barChartConfig.barmode = 'stack';
            }

            PlotlyUtil.renderBarChart(chartId, series, barChartConfig);
        },500);
    };

    $scope.fillBarSeries = function(series, data, label, color){
        angular.forEach(Object.keys(data), function(key){
            if(!series[key]){
                series[key] = {x:[], y:[], name: key}
                if(color){
                    series[key]['marker'] = {color: color}
                }
            }
            series[key].y.push(label);
            series[key].x.push(data[key]);
        });
    };

    $scope.plotHeatMap = function(chartId, data){
        $timeout(function() {
            PlotlyUtil.renderHeatMapChart(chartId, data);
        },500);
    };

    $scope.plotScattedChart = function(chartId, data, hasLine, xTitle, yTitle){
        $timeout(function() {
            var scattedChartConfig = {
                margin: {t: 15},
                //xaxis: {tickformat : "%d/%m/%Y"},
                xaxis: {title: xTitle},
                yaxis: {range: [-0.1, 1.1], title: yTitle}
            };
            PlotlyUtil.renderScattedChart(chartId, data, scattedChartConfig, hasLine);
        },500);
    };

    $scope.onChangeWordcloudParameter = function(cloudType){

        var statistics = null;
        var statisticsByLabel = [];

        var getWordStatistcs = function(value, valueType, statsType, statsDimension){

            var labelsToUse = [];

            if(value == 'ALL'){
                labelsToUse = Object.keys($scope.statisticsMap['words']['all'].all[valueType]).sort();
            }else{
                labelsToUse.push(value);
            }

            var result = [];

            angular.forEach(labelsToUse, function(label){
                var statistics = $scope.statisticsMap['words']['all'].all[valueType][label][statsType][statsDimension];

                statisticsByLabel[label] = statistics;

                angular.forEach(Object.keys(statistics), function(key){
                    if(!result[key]){
                        result[key] = statistics[key]
                    }else{
                        result[key] += statistics[key]
                    }
                });
            });

            return result
        };

        var statistics = [];
        
        if (cloudType == 'TAG'){

            statistics = getWordStatistcs($scope.selection.wordCloudTag, 'tags',
                $scope.selection.wordCloudTagType, $scope.selection.wordCloudTagDimension);

        }else if (cloudType == 'RELATION'){

            statistics = getWordStatistcs($scope.selection.wordCloudRelation, 'relations',
                $scope.selection.wordCloudRelationType, $scope.selection.wordCloudRelationDimension);
        }

        $timeout(function(){

            //console.log(statisticsByLabel);

            var wordEntries = [];

            angular.forEach(Object.keys(statistics), function(key){
                wordEntries.push({text: key, size: statistics[key]});
            });

            var wordEntriesByLabel = [];
            angular.forEach(Object.keys(statisticsByLabel).sort(), function(label){
                wordEntriesByLabel[label] = [];
                angular.forEach(Object.keys(statisticsByLabel[label]), function(key){
                    wordEntriesByLabel[label].push({text: key, size: statistics[key]});
                });
            });

            wordEntries.sort(function (a, b){
                return b.size - a.size;
            });

            if (cloudType == 'TAG'){
                $scope.tagWordEntries = wordEntries;
            }else if (cloudType == 'RELATION'){
                $scope.relationWordEntries = wordEntries;
            }

            var containerId = cloudType == 'TAG' ? 'tagwordcloud' : 'relationwordcloud';

            var container = document.getElementById(containerId);
            while(container.firstChild) {
                container.removeChild(container.firstChild);
            }

            var d3WordEntries = angular.copy(wordEntries);

            console.log(d3WordEntries);

            d3.wordcloud().size([760, 400])
                .selector('#' + containerId)
                .scale('sqrt')
                .fill(d3.scale.ordinal().range(["#884400", "#448800", "#888800", "#444400"]))
                .words(d3WordEntries).start();

            var series = [];
            var accumulatedByLabel = [];

            angular.forEach(Object.keys(wordEntriesByLabel).sort(), function(label){
                accumulatedByLabel[label] = 0;
                series.push({
                    y: 0,
                    x: 0,
                    text: '',
                    name: label
                });
                angular.forEach(wordEntriesByLabel[label].sort(
                    function(a, b){return b.size-a.size}), function(wordEntry, index){
                    accumulatedByLabel[label] += wordEntry.size;
                    series.push({
                        y: accumulatedByLabel[label],
                        x: index + 1,
                        text: wordEntry.text,
                        name: label
                    });
                });
            });

            angular.forEach(series, function(value){
                value.y = value.y/accumulatedByLabel[value.name];
            });

            if (cloudType == 'TAG'){
                $scope.plotScattedChart('tagFrequencyCurve', series, true, 'nth subsentence', 'accumulated frequency');
            }else if (cloudType == 'RELATION'){
                $scope.plotScattedChart('relationFrequencyCurve', series, true, 'nth subsentence', 'accumulated frequency');
            }

            //console.log(series);

        }, 500);

    };

    $scope.onShowCommentsModal = function(){
        $scope.commentsModalBoxBlockUI.start();
        DocumentPackageService.getComments($scope.selection.documentPackage.id).then(function(response) {
            $scope.documentPackageComments = response.data;
            angular.forEach($scope.documentPackageComments, function (doc) {
                angular.forEach(doc.collaborations, function (collaboration) {
                    collaboration.collaborator = $scope.collaboratorsByEmail[collaboration.collaborator];
                    collaboration.collaboratorLabel = collaboration.collaborator.lastName+', '+collaboration.collaborator.firstName;
                });
            });
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
            console.info(response);
        }).finally(function(){
            $scope.commentsModalBoxBlockUI.stop();
        });
    };

    $scope.downloadTable = function(tableId, caption){
        LatexUtil.downloadTable(tableId, caption)
    };

    $scope.onSelectRandomAnnotation = function(){

    };

}]);