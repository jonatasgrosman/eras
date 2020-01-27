angular.module('ERAS').directive("limitTo", [ function() {

	return {
		restrict : 'A',
		require : 'ngModel',
		link : function(scope, elem, attrs, ctrl) {
			attrs.$set("ngTrim", "false");
			var maxlength = parseInt(attrs.limitTo, 10);
			ctrl.$parsers.push(function(value) {
				if (value && value.length > maxlength) {
					value = value.substr(0, maxlength);
					ctrl.$setViewValue(value);
					ctrl.$render();
				}
				return value;
			});
		}
	}

} ]);