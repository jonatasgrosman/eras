angular.module('ERAS').factory('ArrayUtil', [function() {

    var _remove = function(array, value) {
        var index = array.indexOf(value);
        if (index > -1) {
            array.splice(index, 1);
        }
    }

	var _contains = function(array, obj) {
	    var i = array.length;
	    while (i--) {
	       if (array[i] === obj) {
	           return true;
	       }
	    }
	    return false;
	}

	var _sanitize = function(array){
        return array.filter(function(e){ return e === 0 || e });
    }

    var _filter = function(array, filterFun = function(array){
      return array;
    }){
      return array.filter(filterFun);
    }

    var _arrayToString = function(array, interStr){
        var string = '';
        var i = 0;
        for(i = 0; i < array.length - 1; i++){
            string += array[i] + interStr;
        }
        string += array[array.length-1];
        return string;
    }

    var _fromMap = function(map){
        var arrayToReturn = [];
        angular.forEach(Object.keys(map), function(key){
            arrayToReturn.push(map[key]);
        });
        return arrayToReturn;
    }

    return {
    	remove : _remove,
    	contains : _contains,
    	sanitize : _sanitize,
        filter: _filter,
        arrayToString: _arrayToString,
        fromMap : _fromMap
    }

}]);
