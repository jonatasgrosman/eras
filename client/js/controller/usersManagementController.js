angular.module('ERAS').controller('UsersManagementController', ['$scope', 'UserService', 'blockUI', 'PNotifyUtil',
                                                                function($scope, UserService, blockUI, PNotifyUtil) {
	
	$scope.init = function() {
		$scope.userManagementBoxBlockUI = blockUI.instances.get('userManagementBox');

        $scope.userManagementBoxBlockUI.start();
		UserService.list().then(function(response) {
		    $scope.users = response.data;
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.userManagementBoxBlockUI.stop();
        });

        $scope.roles = ['ADMIN', 'COLLABORATOR', 'USER'];

	}

	$scope.initAddUserMode = function() {
	    $scope.originalUser = null;
	    $scope.user = {}
	}
	
    $scope.initEditUserMode = function(user) {
        $scope.originalUser = user;
        $scope.user = angular.copy(user);
    }

    $scope.saveUser = function() {

        var action = $scope.originalUser ? UserService.update : UserService.insert

        $scope.userManagementBoxBlockUI.start();
        action($scope.user).then(function(response) {
            if($scope.originalUser){
                PNotifyUtil.showSuccess(':)', 'User updated');
                $scope.originalUser.firstName = $scope.user.firstName;
                $scope.originalUser.lastName = $scope.user.lastName;
                $scope.originalUser.role = $scope.user.role;
            }else{
                PNotifyUtil.showSuccess(':)', 'User added');
                $scope.users.push($scope.user);
            }
        }, function(response) {
        	PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.originalUser = null;
		    $scope.user = null;
            $scope.userManagementBoxBlockUI.stop();
        });

    }

    $scope.init();
    
}]);