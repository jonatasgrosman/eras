angular.module('ERAS').controller('LoginController', ['$scope', '$state', 'AuthService', '$rootScope',
                                                    function($scope, $state, AuthService, $rootScope) {
	
	$scope.init = function() {		
		$scope.user = {email:'', password:''}
		$scope.loginError = null;
	}
	
    $scope.login = function() {
        AuthService.login($scope.user.email, $scope.user.password).then(function(response) {
            //$rootScope.loggedUser = response;
        	$state.transitionTo('home');
        }, function(response) {
        	$scope.loginError = response.status;
        });
    }

    $scope.init();
    
}]);
