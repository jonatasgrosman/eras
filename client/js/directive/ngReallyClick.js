//http://stackoverflow.com/questions/22113456/modal-confirmation-as-an-angular-ui-directive
angular.module('ERAS').directive('ngReallyClick', ['$uibModal', function($uibModal) {

      var ModalInstanceCtrl = function($scope, $uibModalInstance) {
        $scope.ok = function() {
          $uibModalInstance.close();
        };

        $scope.cancel = function() {
          $uibModalInstance.dismiss('cancel');
        };
      };

      return {
        restrict: 'A',
        scope:{
          ngReallyClick:"&",
          item:"="
        },
        link: function(scope, element, attrs) {
          element.bind('click', function() {
            var message = attrs.ngReallyMessage || "Are you sure ?";

            /*
            //This works
            if (message && confirm(message)) {
              scope.$apply(attrs.ngReallyClick);
            }
            //*/

            //*This doesn't works
            var modalHtml = '<div class="modal-body">' + message + '</div>';
            modalHtml += '<div class="modal-footer"><button class="btn btn-success" ng-click="ok()">YES</button><button class="btn btn-danger" ng-click="cancel()">NO</button></div>';

            var modalInstance = $uibModal.open({
              template: modalHtml,
              controller: ModalInstanceCtrl,
              backdropClass: 'backdrop-alert',
              windowClass: 'alert',
            });

            modalInstance.result.then(function() {
              scope.ngReallyClick({item:scope.item}); //raise an error : $digest already in progress
            }, function() {
              //Modal dismissed
            });
            //*/

          });

        }
      }
    }
  ]);