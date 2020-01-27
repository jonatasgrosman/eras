angular.module('ERAS').filter('dropDigits', ['$interval', function ($interval){

    return function(floatNum, maxLength) {
        return String(floatNum)
            .split('.')
            .map(function (d, i) { return i ? d.substr(0, maxLength) : d; })
            .join('.');
    };

}]);