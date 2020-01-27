angular.module('ERAS').factory('DateUtil', [function() {

	var _format = function(date, pattern) {

        formattedDate = pattern.replace('yyyy', date.getFullYear().toString());

        var MM = (date.getMonth() + 1).toString(); // getMonth() is zero-based
        MM = MM.length > 1 ? MM : '0' + MM;
        formattedDate = formattedDate.replace('MM', MM);

        var dd = date.getDate().toString();
        dd = dd.length > 1 ? dd : '0' + dd;
        formattedDate = formattedDate.replace('dd', dd);

        var hh = date.getHours().toString();
        if(date.getHours() < 10){
            hh = '0' + hh
        }
        formattedDate = formattedDate.replace('hh', hh);

        var mm = date.getMinutes().toString();
        if(date.getMinutes() < 10){
            mm = '0' + mm
        }
        formattedDate = formattedDate.replace('mm', mm);

        var ss = date.getSeconds().toString();
        if(date.getSeconds() < 10){
            ss = '0' + ss
        }
        formattedDate = formattedDate.replace('ss', ss);

        return formattedDate;
    }

    var _get_difference_as_string = function(date1, date2){

        var time1 = Date.parse(date1);
        var time2 = Date.parse(date2);
        var difference = Math.abs(time1 - time2);

        // get total seconds between the times
        var delta = difference / 1000;

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


    return {
    	format : _format,
    	get_difference_as_string : _get_difference_as_string
    }

}]);