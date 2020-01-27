angular.module('ERAS').controller('AppController', ['$scope', '$state', 'AuthService', '$rootScope',
                                                    function($scope, $state, AuthService, $rootScope) {
	
	$scope.init = function() {
	    $scope.loggedUser = AuthService.getLoggedUser();
		$scope.user = {email:'', password:''}
		$scope.loginError = null;
	}

    $scope.login = function() {
        AuthService.login($scope.user.email, $scope.user.password).then(function(response) {
            $scope.loggedUser = AuthService.getLoggedUser();
        	$scope.init();
        }, function(response) {
        	$scope.loginError = response.status;
        });
    }

    $scope.logout = function() {
        AuthService.logout();
        $scope.loggedUser = null;
        $state.transitionTo('home');
    }

    $scope.goToSupplierProfileEdit = function() {
        $state.transitionTo('supplier-profile-edit');
    }

    $scope.goToPasswordUpdate = function() {
        $state.transitionTo('password-update');
    }

    $scope.init();
    
}]);
