angular.module('ERAS').factory('LocalStorageService', [function() {

    return {

        clear: function() {
            return localStorage.clear();
        },

        get: function(key) {
            return JSON.parse(localStorage.getItem(key));
        },

        set: function(key, data) {
            return localStorage.setItem(key, JSON.stringify(data));
        },

        delete: function(key) {
            return localStorage.removeItem(key);
        },

        getAll: function() {
        	var archive = {}, 
	        keys = Object.keys(localStorage),
	        i = keys.length;

		    while ( i-- ) {
		        archive[ keys[i] ] = localStorage.getItem(keys[i]);
		    }

		    return archive;
        }

    };

}]);