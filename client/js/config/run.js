angular.module('ERAS').run(['$rootScope', '$cacheFactory', '$browser', '$window', '$state', 'GentelellaThemeUtil', 'AuthService',  'Constants',
     function($rootScope, $cacheFactory, $browser, $window, $state, GentelellaThemeUtil, AuthService, Constants) {
	
		// override the $browser.baseHref() method so it returns "/" without needing to use a <base href="/"> element
		// in the head of the document (which causes problems with SVG patterns amongst other things)
		$browser.baseHref = function() {return Constants.BASE_HREF};

		/*AuthService.verifyToken().then(function(){
			$rootScope.loggedUser = AuthService.getLoggedUser();
		});*/
		
		// Execute every time a state change begins
		$rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
			
			// handling template cache
			// If the state we are headed to has cached template views
			if (typeof (toState) !== 'undefined' && typeof (toState.views) !== 'undefined') {
				// Loop through each view in the cached state
				for (var key in toState.views) {
					// Delete template from cache
					//console.log("Delete cached template: " + toState.views[key].templateUrl);
					$cacheFactory.get('templates').remove(toState.views[key].templateUrl);
				}
			}

		    //AuthService.verifyToken().then(function(response){ // valid token
            var loggedUser = AuthService.getLoggedUser();

            if(toState.data.roles.length && !loggedUser && 'login' != toState.name){
                event.preventDefault();
                $state.transitionTo('login');

            }else if((['login','forgot-password'].indexOf(toState.name) != -1 && loggedUser) ||
                     (toState.data.roles.length && toState.data.roles.indexOf(loggedUser.role) == -1)){
                event.preventDefault();
                $state.transitionTo('home');

            }else{
                $rootScope.$state = toState;
            }

            /*}, function(response){ // invalid token
                AuthService.logout();
                event.preventDefault();
                if('login' != toState.name){
                    $state.transitionTo('login');
                }
            });*/

			/*var loggedUser = AuthService.getLoggedUser();

			if(toState.data.roles.length && !loggedUser){
			    event.preventDefault();
                $state.transitionTo('login');
            }else if((['login','forgot-password'].indexOf(toState.name) != -1 && loggedUser) ||
                     (toState.data.roles.length && toState.data.roles.indexOf(loggedUser.role) == -1)){
                event.preventDefault();
                $state.transitionTo('home');
            }else{
                $rootScope.$state = toState;
            }*/

		});
		
		$rootScope.$on('$stateChangeSuccess',function(event, toState, toParams, fromState, fromParams){

			/*if ($window.ga){//google analytics
				var pageUrl = Constants.ROOT_URL+toState.url.split('?')[0];
				$window.ga('send', 'pageview', { page: pageUrl});//send event
			}*/

			/*if(toState.name != 'login' && !AuthService.getLoggedUser()){
                $state.transitionTo('login');
            }*/

            //GentelellaThemeUtil.refresh();

			angular.element("html, body").animate({ scrollTop: 0 }, 0);

		});

    }
]);