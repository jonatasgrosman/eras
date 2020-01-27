angular.module('ERAS').controller('RecoveryPasswordController', ['$scope', '$state', 'UserService', '$rootScope', '$stateParams', 'blockUI',
                                                                function($scope, $state, UserService, $rootScope, $stateParams, blockUI) {
	
	$scope.init = function() {
		$scope.loginError = null;
		$scope.recovery = {
		    email : $stateParams.email,
		    token : $stateParams.token,
		}
		$scope.emailSent = false;
		$scope.recoveryPasswordBoxBlockUI = blockUI.instances.get('recoveryPasswordBox');
	}
	
    $scope.recoveryPassword = function() {
        $scope.recoveryPasswordBoxBlockUI.start();
        UserService.recoveryPassword($scope.recovery.email).then(function(response) {
            $scope.emailSent = true;
            $scope.loginError = null;
        }, function(response) {
        	$scope.loginError = response.status;
        }).finally(function(){
            $scope.recoveryPasswordBoxBlockUI.stop();
        });
    }

    $scope.resetPassword = function() {
        $scope.recoveryPasswordBoxBlockUI.start();
        UserService.resetPassword($scope.recovery.email, $scope.recovery.token, $scope.recovery.newPassword).then(function(response) {
            $state.transitionTo('login');
        }, function(response) {
        	$scope.loginError = response.status;
        	$scope.recovery.token = null;
        }).finally(function(){
            $scope.recoveryPasswordBoxBlockUI.stop();
        });
    }

    $scope.init();
    
}]);
