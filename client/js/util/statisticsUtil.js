angular.module('ERAS').factory('StatisticsUtil', [function() {

    var _sum = function(data){
        return data.reduce(function(sum, value){
            return sum + value;
        }, 0);
    }


    var _standardDeviation = function(data){
        var avg = _average(data);

        var squareDiffs = data.map(function(value){
            var diff = value - avg;
            var sqrDiff = diff * diff;
            return sqrDiff;
        });

        var avgSquareDiff = _average(squareDiffs);

        var stdDev = Math.sqrt(avgSquareDiff);
        return stdDev;
    }

    var _average = function(data){
        var sum = _sum(data)
        var avg = sum / data.length;
        return avg;
    }

    return {
        sum : _sum,
        standardDeviation : _standardDeviation,
        average : _average
    }

}]);
