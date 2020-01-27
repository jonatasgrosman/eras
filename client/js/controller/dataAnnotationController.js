angular.module('ERAS').controller('DataAnnotationController',
    ['$scope', '$window', '$document', '$timeout', 'blockUI', 'PNotifyUtil', 'PlotlyUtil', 'AuthService', 'ProjectService', 'DocumentPackageService', 'OntologyUtil',
    function($scope, $window, $document, $timeout, blockUI, PNotifyUtil, PlotlyUtil, AuthService, ProjectService, DocumentPackageService, OntologyUtil) {

    $scope.init = function() {
        $scope.documentPackageBoxBlockUI = blockUI.instances.get('documentPackageBox');
        $scope.documentBoxBlockUI = blockUI.instances.get('documentBox');

        $scope.listDocumentPackages();
        $scope.selection = {documentPackage:null}
        //$scope.loadSelfAgreementChart();
    }

    $scope.listDocumentPackages = function() {
        $scope.documentPackageBoxBlockUI.start();
        DocumentPackageService.listByCollaborator(AuthService.getLoggedUser()).then(function(response) {
            $scope.documentPackages = response.data;
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
            console.info(response);
        }).finally(function(){
            $scope.documentPackageBoxBlockUI.stop();
        });
    }

    $scope.loadStatistics = function(successCallback) {
        $scope.documentPackageBoxBlockUI.start();
        $scope.documentBoxBlockUI.start();

        DocumentPackageService.getStatistics(
            $scope.selection.documentPackage.id, AuthService.getLoggedUser().email,
            null, null, null,
            null, null, $scope.selection.documentPackage.showSelfAgreementFeedback
        ).then(function(response) {

            var statistics = response.data;
           
            previousCollaboration = $scope.selection.collaboration
            if($scope.selection.documentPackage.showSelfAgreementFeedback && (
                !previousCollaboration || previousCollaboration.type == 'reannotation')){
                                
                $scope.loadSelfAgreementChart(statistics);
            }

            DocumentPackageService.getGroupByCollaboratorEmail(
                $scope.selection.documentPackage.id,
                AuthService.getLoggedUser().email
            ).then(function(response) {

                $scope.statistics = statistics;
                $scope.group = response.data;

                var totalDone = $scope.statistics.uncheckedDone + $scope.statistics.precheckedDone + $scope.statistics.checkedDone;
                var totalUndone = $scope.statistics.uncheckedUndone + $scope.statistics.precheckedUndone + $scope.statistics.checkedUndone;

                var totalToReannotate = $scope.group.reannotationStep ? parseInt((totalDone + $scope.statistics.uncheckedUndone)/$scope.group.reannotationStep) : 0;

                $scope.statistics.total = $scope.group.warmUpSize + totalDone + totalUndone + totalToReannotate;
                $scope.statistics.totalDone = totalDone + $scope.statistics.precheckedUndone + $scope.statistics.checkedUndone + $scope.statistics.warmUp + $scope.statistics.reannotation;

                $scope.statistics.donePercentual = parseFloat(($scope.statistics.totalDone/$scope.statistics.total).toFixed(4)) * 100;

                if(successCallback){
                    successCallback();
                }

            }, function(response) {
                PNotifyUtil.showError(':(', 'Something unexpected happened');
                console.info(response);
            }).finally(function(){
                $scope.documentPackageBoxBlockUI.stop();
                $scope.documentBoxBlockUI.stop();
            });

        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
            console.info(response);
            $scope.documentPackageBoxBlockUI.stop();
            $scope.documentBoxBlockUI.stop();
        });
    };

    $scope.onShowOntologyModal = function() {
        /*$scope.documentBoxBlockUI.start();
        ProjectService.getOntologyTree($scope.selection.documentPackage.project.id).then(function(response) {
            $scope.ontologyEntityTree = OntologyUtil.getTree(response.data, 'entity');
            $scope.ontologyRelationTree = OntologyUtil.getTree(response.data, 'relation', true);
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.documentBoxBlockUI.stop();
        });*/
    };

    /*$scope.loadOntologyMap = function(successCallback) {
        $scope.documentBoxBlockUI.start();

        ProjectService.getOntologyMap(
            $scope.selection.documentPackage.project.id
        ).then(function(response) {
            $scope.ontologyMap = response.data;

            if(successCallback){
                successCallback();
            }

        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        }).finally(function(){
            $scope.documentBoxBlockUI.stop();
        });
    }*/

    $scope.loadCollaborations = function(){
        $scope.documentBoxBlockUI.start();

        DocumentPackageService.getCollaboration(
            $scope.selection.documentPackage.id
        ).then(function(response) {
            $scope.collaborations = response.data;

            if($scope.collaborations.length > 0){
                $scope.selection.collaboration = $scope.collaborations[0]
                $scope.loadAnnotator();
            }

        }, function(response) {
            if(response.status != 404){
                PNotifyUtil.showError(':(', 'Something unexpected happened');
                console.info(response);
            }
        }).finally(function(){
            $scope.documentBoxBlockUI.stop();
        });
    }

    $scope.loadNextCollaboration = function() {

        $scope.documentBoxBlockUI.start();

        DocumentPackageService.getCollaboration(
            $scope.selection.documentPackage.id,
            $scope.selection.collaboration ? $scope.selection.collaboration.id : null
        ).then(function(response) {

            $scope.selection.collaboration = response.data;
            $scope.loadAnnotator();
            
        }, function(response) {
            if(response.status != 404){
                PNotifyUtil.showError(':(', 'Something unexpected happened');
                console.info(response);
            }
        }).finally(function(){
            $scope.documentBoxBlockUI.stop();
        });

    }

    $scope.onChangeSelectedDocumentPackage = function(){

        $scope.selection.collaboration = null

        $scope.loadStatistics(function(){

            if($scope.statistics.donePercentual != 100){
                if($scope.selection.documentPackage.randomAnnotation){
                    $scope.loadNextCollaboration()
                }else{
                    var myNode = document.getElementById('annotatorContainer')
                    while (myNode.firstChild) {
                        myNode.removeChild(myNode.firstChild);
                    }
                    $scope.loadCollaborations()
                }
            }

            //CREATING ANNOTATOR ENTITIES
            var updateEntity = function(entity, parent){
				if(!entity.enabled){
					entity.disabled = true
				}else if(parent){
					parent.hasEnabledChildren = true
				}
				if(entity.relations){
					entity.relations = entity.relations.filter((relation)=>{
						return relation.enabled
					})
				}

				if(entity.children){
					entity.children.forEach(child => {
						updateEntity(child, entity)
						if(child.hasEnabledChildren){
							entity.hasEnabledChildren = true
						}
					})
					entity.children = entity.children.filter(child => {
						return child.hasEnabledChildren || child.enabled
					})
				}
			}
			
			var entities = angular.copy($scope.selection.documentPackage.project.entities)

			entities.forEach(e => updateEntity(e))
			entities = entities.filter(e => e.hasEnabledChildren || e.enabled)

			$scope.selection.documentPackage.project.entities = entities
        });
    }

    $scope.loadSelectedAnnotator = function(collaboration){
        $scope.selection.collaboration = collaboration
        $scope.loadAnnotator()
    }

    $scope.loadAnnotator = function() {

        var config = {
            entities : $scope.selection.documentPackage.project.entities,
            status: ['UNDONE','DONE'],
            onChange : function(collaboration, changeLog, undoCallback){

                $scope.documentBoxBlockUI.start();

                DocumentPackageService.updateCollaboration(
                    $scope.selection.documentPackage.id,
                    collaboration,
                    changeLog
                ).then(function(response) {
                    collaboration.stateKey = response.data;
                    if(collaboration.status == 'DONE'){
                        $scope.loadStatistics(function(){

                            if($scope.statistics.totalDone < $scope.statistics.total){
                                if($scope.selection.documentPackage.randomAnnotation){
                                    $scope.loadNextCollaboration()
                                }else{
                                    $scope.loadCollaborations()
                                    var myNode = document.getElementById('annotatorContainer')
                                    while (myNode.firstChild) {
                                        myNode.removeChild(myNode.firstChild);
                                    }
                                }
                            }
                        });
                    }
                }, function(response) {
                    undoCallback();
                    PNotifyUtil.showError(':(', 'Something unexpected happened');
                }).finally(function(){
                    $scope.documentBoxBlockUI.stop();
                });

            },
            showIndex : false,
            showMetadata : false,
            mode : 'annotation'
        }

        $scope.selection.collaboration.updateToken = '123';

        AnnotatorJS.render("annotatorContainer", $scope.selection.collaboration, config);
        $document.scrollTo(angular.element('#annotatorContainer'), 70, 1000);

    }

    $scope.onShowAnnotationGuidelinesModal = function() {
        //$window.open('https://www.dropbox.com/s/01za39ci0nab3tr/guide-KnowledgeStudio.pdf?dl=0', "popup", "width=1000,height=700,left=300,top=200");
        PDFObject.embed(ProjectService.getAnnotationGuidelinesFileUrl($scope.selection.documentPackage.project.id), "#annotationGuidelinesPdfContainer");
    }

    $scope.loadSelfAgreementChart = function(statistics){

        x = []
        y = []

        statistics.selfAgreement.forEach(function(v, i){
            y.push(v.cohenKappa.k)
            x.push(i)
        })

        $timeout(function() {

            var trace1 = {
                x: x, // [0, 1, 2, 3, 4, 5, 6, 7],
                y: y, // [0.2, 0.2, 0.4, 0.6, 0.8, 0.7, 0.9, 0.8],
                type: 'scatter',
                line: {
                    shape: 'spline'
                },
                marker: {
                    size: 2
                }
            };
            
            var layout = {
                xaxis: {
                    autorange: false,
                    showgrid: false,
                    zeroline: true,
                    showline: false,
                    ticks: '',
                    showticklabels: false
                },
                yaxis: {
                    range: [-1,1],
                    showgrid: false,
                    showline: false,
                    zeroline: false,
                    ticks: '',
                    showticklabels: false
                },
                //width: 500,
                height: 50,
                margin: {
                    l: 5,
                    r: 40,
                    b: 5,
                    t: 5,
                    pad: 0
                },
                annotations: [
                    {
                        x: 0,
                        y: 1,
                        xanchor: 'right',
                        text: 'good',
                        showarrow: false,
                        font: {
                            family: 'Courier New',
                            size: 10
                        },
                    },
                    {
                        x: 0,
                        y: -1,
                        xanchor: 'right',
                        text: 'bad',
                        showarrow: false,
                        font: {
                            family: 'Courier New',
                            size: 10
                        },
                    },
                    {
                        x: 6,
                        xanchor: 'left',
                        y: $scope.selection.documentPackage.selfAgreementFeedbackGoal || 0.5,
                        text: 'goal',
                        showarrow: false,
                        xref: 'x',
                        yref: 'y',
                        font: {
                            family: 'Courier New',
                            size: 10,
                            color: 'green'
                        },
                    }
                ],
                shapes: [
                {
                    type: 'line',
                    x0: 0,
                    y0: $scope.selection.documentPackage.selfAgreementFeedbackGoal || 0.5,
                    x1: 7,
                    y1: $scope.selection.documentPackage.selfAgreementFeedbackGoal || 0.5,
                    line:{
                        color: 'green',
                        width: 1,
                        dash:'dash'
                    }
                }
                ]
            }

            config = { displayModeBar: false, responsive: true }

            PlotlyUtil.render('selfAgreementFeedbackChart', [trace1], layout, config);
            
            var goal = $scope.selection.documentPackage.selfAgreementFeedbackGoal;
            if(y.length > 2 && y[y.length - 2] <= goal && y[y.length - 1] <= goal){
                $('#selfAgreementFeedbackChart').parent().css('background-color','#ff8080');
                $("#selfAgreementFeedbackChart").fadeIn(1000).fadeOut(1000).fadeIn(1000).fadeOut(1000).fadeIn(1000);
                $timeout(function() {$('#selfAgreementFeedbackChart').parent().css('background-color','none');}, 6000);
            }

        },500);

    }

    $scope.init();

}]);