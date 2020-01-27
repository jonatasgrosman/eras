angular.module('ERAS').factory('Base64Util', [function() {

    var _stringToBase64 = function(str) {
        return window.btoa(unescape(encodeURIComponent(str)));
    }

    var _base64ToString = function(str) {
        return decodeURIComponent(escape(window.atob(str)));
    }

    return {
    	stringToBase64 : _stringToBase64,
    	base64ToString : _base64ToString
    }

}]);