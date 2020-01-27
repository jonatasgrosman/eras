angular.module('ERAS').directive("dlKeyCode", [ function() {

	return {
		restrict: 'A',
		link : function($scope, $element, $attrs) {

			$element.bind("change", function(event){

				if($element.data('old-value') > $attrs.max){
					$scope.$apply(function(){
						$element.val();
					});
				}

			});

		}
	};

} ]);