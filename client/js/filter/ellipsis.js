angular.module('ERAS').filter("ellipsis", [ function() {

    return function (input, maxLength) {
        if(!maxLength){
            maxLength = 10;
        }
        if (input) {
            return input.substring(0, maxLength) + '...';
        }
    }

} ]);