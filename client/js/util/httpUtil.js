angular.module('ERAS').factory('HttpUtil', [function() {

    var _addParameter = function(url, parameterKey, parameterValue){
        return url + (url.indexOf('?') != -1 ? '&'+parameterKey+'=' + parameterValue : '?'+parameterKey+'=' + parameterValue);
    }

    return {
    	addParameter : _addParameter
    }

}]);
