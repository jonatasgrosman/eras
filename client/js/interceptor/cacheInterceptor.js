angular.module('ERAS').factory('CacheInterceptor', ['Constants', function(Constants) {

	return {
		request: function(config) {
			if(config.url.indexOf('view/') > -1){
                var separator = config.url.indexOf('?') === -1 ? '?' : '&';
                var v = Constants.STAGE == 'DEVELOPMENT' ? Math.random() : Constants.VERSION;
                config.url = config.url + separator + 'v=' + v;
            }

            return config;
		}
	}

}])