angular.module('ERAS').controller('ProfileController', ['$scope', '$state', 'UserService', 'AuthService', '$rootScope', 'blockUI', 'PNotifyUtil',
                                                        function($scope, $state, UserService, AuthService, $rootScope, blockUI, PNotifyUtil) {

	$scope.init = function() {
	    var loggedUser = AuthService.getLoggedUser();
		$scope.profile = {firstName:loggedUser.firstName, lastName:loggedUser.lastName}
		$scope.passwordChangeRequest = {currentPassword:null, newPassword:null, passwordConfirmation:null}

		$scope.profileBoxBlockUI = blockUI.instances.get('profileBox');
		$scope.passwordChangeBoxBlockUI = blockUI.instances.get('passwordChangeBox');

	}
	
    $scope.saveProfile = function() {

        $scope.profileBoxBlockUI.start();

        var user = angular.copy(AuthService.getLoggedUser());
        user.firstName = $scope.profile.firstName;
        user.lastName = $scope.profile.lastName;

        UserService.update(user).then(function(response) {
        	$rootScope.loggedUser.firstName = user.firstName;
        	$rootScope.loggedUser.lastName = user.lastName;
        	AuthService.setLoggedUser(user);

        	PNotifyUtil.showSuccess(':)', 'Profile updated');
        }, function(response) {
            PNotifyUtil.showError(':(', 'Something unexpected happened');
        	console.info(response);
        }).finally(function(){
            $scope.profileBoxBlockUI.stop();
        });


    }

    $scope.changePassword = function() {

        $scope.passwordChangeBoxBlockUI.start();

        UserService.changePassword($scope.passwordChangeRequest.currentPassword, $scope.passwordChangeRequest.newPassword).then(function(response) {
            PNotifyUtil.showSuccess(':)', 'Password changed');
            $scope.passwordChangeRequest = {currentPassword:null, newPassword:null, passwordConfirmation:null}
        }, function(response) {
            if(response.status == 401){
                PNotifyUtil.showWarning(':(', 'Please check the password');
            }else{
                PNotifyUtil.showError(':(', 'Something unexpected happened');
            }
        	console.info(response);

        }).finally(function(){
            $scope.passwordChangeBoxBlockUI.stop();
        });

    }

    $scope.init();
    
}]);
