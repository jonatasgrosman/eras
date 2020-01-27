angular.module('ERAS').factory('UserService', ['$http', 'Constants', function($http, Constants) {

    var _insert = function(user){
    	return $http.post(Constants.AUTHENTICATION_SERVER_URL + '/user', user);
    }

    var _update = function(user){
    	return $http.post(Constants.AUTHENTICATION_SERVER_URL + '/user?email='+user.email, user);
    }

    var _changePassword = function(currentPassword, newPassword){
    	return $http.post(Constants.AUTHENTICATION_SERVER_URL + '/user/change-password',
    	                    {currentPassword: currentPassword, newPassword: newPassword});
    }

    var _recoveryPassword = function(email){
    	return $http.get(Constants.AUTHENTICATION_SERVER_URL + '/user/recovery-password?email='+email);
    }

    var _resetPassword = function(email, token, newPassword){
    	return $http.post(Constants.AUTHENTICATION_SERVER_URL + '/user/reset-password',
    	                    {email: email, token: token, newPassword: newPassword});
    }

    var _list = function(){
    	return $http.get(Constants.AUTHENTICATION_SERVER_URL + '/user');
    }

    return {
        insert : _insert,
    	update : _update,
    	changePassword : _changePassword,
    	recoveryPassword : _recoveryPassword,
		resetPassword : _resetPassword,
    	list : _list
    }

}]);