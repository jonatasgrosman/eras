angular.module('ERAS').factory('AuthService', ['$http', '$q', '$interval', 'Constants', 'LocalStorageService', function($http, $q, $interval, Constants, LocalStorageService) {

    var _tokenUpdater = null,
    	_tokenUpdaterInterval = 60000*5; // 5 minutes in milliseconds

    var _verifyToken = function(){
    	
    	var user = _getLoggedUser();
        
    	if(!user || !user.token){
            return $q.reject("You don't have a token yet!");
        }else{

            var deferred = $q.defer();
            $http.get(Constants.AUTHENTICATION_SERVER_URL + '/auth/verify-token').then(function(response){
                _setLoggedUser(response.data);
                deferred.resolve(_getLoggedUser());
            },function(response){
                _logout();
                deferred.reject(response);
            });

            return deferred.promise;    
        }        
    };

    var _getLoggedUser = function() {

        var user = LocalStorageService.get(Constants.USER_STORAGE_KEY);
        if(user){
            user.isAdmin = user.role === 'ADMIN';
        }
        return user;

    	/*var deferred = $q.defer();
    	_verifyToken().then(function(){
    		_startTokenAutoRefresh();
    	},function(){
    		_stopTokenAutoRefresh();
    	}).finally(function() {    		
    		
    		var user = LocalStorageService.get(Constants.USER_STORAGE_KEY);
    		if(user){
    			user.isAdmin = user.role === 'ADMIN';
    		}
    		
        	deferred.resolve(user);
        });
        return deferred.promise;*/
    }

    var _setLoggedUser = function(user) {
        LocalStorageService.set(Constants.USER_STORAGE_KEY, user);
    }

    var _startTokenAutoRefresh = function(){
        if(!_tokenUpdater){
            _tokenUpdater = $interval(function() {
                $http.get(Constants.AUTHENTICATION_SERVER_URL + '/auth/refresh-token').then(function(response){
                    // :)
                    _setLoggedUser(response.data);
                }, function(){
                    //console.log('Error when update token');
                    //console.log(new Date());
                });
            }, _tokenUpdaterInterval);
        }
    }

    var _stopTokenAutoRefresh = function(){
        $interval.cancel(_tokenUpdater);
        //console.log('token auto refresh was stopped');
        _tokenUpdater = null;
    }

    var _login = function(email, password){

        var deferred = $q.defer();
        var user = {email: email, password: password}

        $http.post(Constants.AUTHENTICATION_SERVER_URL + '/auth/authenticate', user).then(function(response){
            _setLoggedUser(response.data);
            _startTokenAutoRefresh();
            deferred.resolve(_getLoggedUser());
        }, function(response){
            deferred.reject(response);
        });

        return deferred.promise;

    }

    var _logout = function(){
        LocalStorageService.delete(Constants.USER_STORAGE_KEY);
        _stopTokenAutoRefresh();    
    }

    return {
        verifyToken : _verifyToken,
        getLoggedUser : _getLoggedUser,
        setLoggedUser: _setLoggedUser,
        login : _login,
        startTokenAutoRefresh : _startTokenAutoRefresh,
        stopTokenAutoRefresh : _stopTokenAutoRefresh,
		logout : _logout
    }

}]);