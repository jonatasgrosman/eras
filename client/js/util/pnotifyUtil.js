angular.module('ERAS').factory('PNotifyUtil', [function() {

	var _showMessage = function(title, text, type) {
        new PNotify({
            title: title,
            text: text,
            type: type,
            styling: 'bootstrap3'
        });
    }
	
	var _showSuccess = function(title, text) {
	    _showMessage(title, text, 'success')
	}
	var _showInfo = function(title, text) {
	    _showMessage(title, text, 'info')
	}
	var _showWarning = function(title, text) {
	    _showMessage(title, text, 'warning')
	}
	var _showError = function(title, text) {
	    _showMessage(title, text, 'error')
	}
	var _showDark = function(title, text) {
	    _showMessage(title, text, 'dark')
	}

    return {
    	showSuccess : _showSuccess,
    	showInfo : _showInfo,
    	showWarning : _showWarning,
    	showError : _showError,
    	showDark : _showDark
    }

}]);