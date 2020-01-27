angular.module('ERAS').controller('HeaderController', ['$scope', '$state', 'AuthService', '$rootScope',
                                                        function($scope, $state, AuthService, $rootScope) {
	
	$scope.init = function() {		
	}

    $scope.logout = function() {
        AuthService.logout();
        $state.transitionTo('login');
    }

    $scope.init();
    
}]);
