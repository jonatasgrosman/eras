angular.module('ERAS').factory('TokenInterceptor', ['$q', '$window', 'Constants', 'LocalStorageService',
													function($q, $window, Constants, LocalStorageService) {

	return {
		request: function(config) {
			config.headers = config.headers || {};

			var user = LocalStorageService.get(Constants.USER_STORAGE_KEY);

			if (user) {
				config.headers['token'] = user.token;
				config.headers['email'] = user.email;
				//config.headers['Content-Type'] = 'application/json';
			}

			return config || $q.when(config);
		},

		response: function(response) {
			return response || $q.when(response);
		},

		requestError: function(config) {
		  return $q.reject(config);
		},

		responseError: function (response) {
		  if(response.status == 401) {
			LocalStorageService.delete(Constants.USER_STORAGE_KEY);
			if($window.location.hash != '#/login'){
			    $window.location = '/';
			}
		  }
		  if(response.status == 403){
            $window.location = '/';
		  }

		  return $q.reject(response);
		}
	}

}])