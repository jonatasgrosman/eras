angular.module('ERAS').filter('elapsed', ['$interval', function ($interval){

    // trigger digest every 1 second
    $interval(function (){}, 1000);

    var filter = function(date){
        if (!date) return;
        var time = Date.parse(date),
            difference = (new Date()) - time;

        // Seconds (e.g. 32s)
        /*difference /= 1000;
        if (difference < 60) return Math.floor(difference)+'s';

        // Minutes (e.g. 12m)
        difference /= 60;
        if (difference < 60) return Math.floor(difference)+'m';

        // Hours (e.g. 5h)
        difference /= 60;
        if (difference < 24) return Math.floor(difference)+'h';

        // Date (e.g. Dec 2)
        return $filter('date')(time, 'MMM d');*/

        // get total seconds between the times
        var delta = Math.abs(date.getTime() - new Date().getTime()) / 1000;

        // calculate (and subtract) whole days
        var days = Math.floor(delta / 86400);
        delta -= days * 86400;

        // calculate (and subtract) whole hours
        var hours = Math.floor(delta / 3600) % 24;
        delta -= hours * 3600;

        // calculate (and subtract) whole minutes
        var minutes = Math.floor(delta / 60) % 60;
        delta -= minutes * 60;

        // what's left is seconds
        var seconds = delta % 60;  // in theory the modulus is not required

        var finalString = '';
        if(days > 0){
            finalString += parseInt(days) + 'd '
        }
        if(hours > 0){
            finalString += parseInt(hours) + 'h '
        }
        if(minutes > 0){
            finalString += parseInt(minutes) + 'm '
        }
        if(seconds > 0){
            finalString += parseInt(seconds) + 's '
        }

        return finalString
    }

    filter.$stateful = true;
    return filter;

}]);