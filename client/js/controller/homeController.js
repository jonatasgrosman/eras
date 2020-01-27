angular.module('ERAS').controller('HomeController', ['$scope', '$state', 'AuthService', function($scope, $state, AuthService) {
	
	$scope.init = function() {		
		/*if(!AuthService.getLoggedUser()){
		    $state.transitionTo('login');
		}*/
	}

    $scope.init();
    
}]);
