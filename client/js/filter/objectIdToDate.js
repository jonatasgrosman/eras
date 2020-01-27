angular.module('ERAS').filter("objectIdToDate", [ function() {

    return function(input) {
        return new Date(parseInt(input.slice(0,8), 16)*1000);
    }

} ]);