angular.module('ERAS').config(['$httpProvider', '$urlRouterProvider', '$stateProvider', '$locationProvider', '$compileProvider', 'Constants', 'blockUIConfig', 'ivhTreeviewOptionsProvider',
    function($httpProvider, $urlRouterProvider, $stateProvider, $locationProvider, $compileProvider, Constants, blockUIConfig, ivhTreeviewOptionsProvider) {
	    
    $httpProvider.interceptors.push('TokenInterceptor');
    $httpProvider.interceptors.push('CacheInterceptor');

    //$locationProvider.html5Mode(true);
    $urlRouterProvider.otherwise('/');

    $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|data|mailto|chrome-extension):/);

    $stateProvider
    .state('root',{
        abstract: true
    })
    .state('login', {
        url: '/login',
        parent: 'root',
        views: {
            'content@': {
                templateUrl: 'view/login.html',
                controller: 'LoginController'
            }
        },
        data: {
            title: 'Login',
            description : 'Login',
            roles : []
        }

    })
    .state('recovery-password', {
        url: '/recovery-password?token&email',
        parent: 'root',
        views: {
            'content@': {
                templateUrl: 'view/recovery-password.html',
                controller: 'RecoveryPasswordController'
            }
        },
        data: {
            title: 'Recovery password',
            description : 'Recovery password',
            roles : []
        }

    })
    .state('app',{
        parent: 'root',
        abstract: true,
        views: {
            'content@': {
                templateUrl: 'view/app.html',
                controller: 'AppController'
            }
        }/*,
        resolve: {
            loggedUser: ['AuthService', '$q', function(AuthService, $q) {
                console.info('1');
            	return AuthService.verifyToken();
            }]
        }*/
    })
    .state('home', {
      	url: '/',
      	parent: 'app',
      	views: {
            'appBody@app': {
                templateUrl: 'view/home.html',
                controller: 'HomeController'
            }
      	},
      	data: {
      		title: 'Home',
		    description : 'Home Page',
		    roles : ['USER', 'ADMIN', 'COLLABORATOR']
      	},
		/*resolve: {
            categories: ['ServiceService', '$q', function(ServiceService, $q) {             	
            	return defaultServiceResolver(ServiceService.getCategories(), $q);
            }]
        }*/
    
    })
    .state('profile', {
        url: '/profile',
        parent: 'app',
        views: {
            'appBody@app': {
                templateUrl: 'view/profile.html',
                controller: 'ProfileController'
            }
        },
        data: {
            title: 'Profile',
            description : 'Profile',
            roles : ['USER', 'ADMIN', 'COLLABORATOR']
        }
    
    })
    .state('users-management', {
        url: '/users-management',
        parent: 'app',
        views: {
            'appBody@app': {
                templateUrl: 'view/users-management.html',
                controller: 'UsersManagementController'
            }
        },
        data: {
            title: 'Users Management',
            description : 'Users Management',
            roles : ['ADMIN']
        }

    })
    .state('projects-management', {
        url: '/projects-management',
        parent: 'app',
        views: {
            'appBody@app': {
                templateUrl: 'view/projects-management.html',
                controller: 'ProjectsManagementController'
            }
        },
        data: {
            title: 'Projects Management',
            description : 'Projects Management',
            roles : ['ADMIN','USER']
        }

    })
    .state('data-management', {
        url: '/data-management',
        parent: 'app',
        views: {
            'appBody@app': {
                templateUrl: 'view/data-management.html',
                controller: 'DataManagementController'
            }
        },
        data: {
            title: 'Data Management',
            description : 'Data Management',
            roles : ['ADMIN','USER']
        }

    })
    .state('data-annotation', {
        url: '/data-annotation',
        parent: 'app',
        views: {
            'appBody@app': {
                templateUrl: 'view/data-annotation.html',
                controller: 'DataAnnotationController'
            }
        },
        data: {
            title: 'Data Annotation',
            description : 'Data Annotation',
            roles : ['ADMIN','USER','COLLABORATOR']
        }

    });
	
    // Change the default delay to 100ms before the blocking is visible
    //blockUIConfig.delay = 100;
	
    blockUIConfig.message = '';
    blockUIConfig.autoBlock = false;
    blockUIConfig.autoInjectBodyBlock = false;
    blockUIConfig.template = '<div class=\"block-ui-overlay\"></div><div class=\"block-ui-message-container\" aria-live=\"assertive\" aria-atomic=\"true\"><div class=\"block-ui-message\" ng-class=\"$_blockUiMessageClass\"><i class="fa fa-refresh fa-spin fa-3x fa-fw"></i>{{ state.message }}</div></div>';

    ivhTreeviewOptionsProvider.set({
        idAttribute: 'id',
        labelAttribute: 'label',
        childrenAttribute: 'children',
        selectedAttribute: 'selected',
        useCheckboxes: false,
        expandToDepth: 0,
        indeterminateAttribute: '__ivhTreeviewIndeterminate',
        expandedAttribute: '__ivhTreeviewExpanded',
        defaultSelectedState: false,
        validate: true,
        /*twistieExpandedTpl: '(-)',
        twistieCollapsedTpl: '(+)',
        twistieLeafTpl: 'o'*/
        twistieCollapsedTpl: '<span class="glyphicon glyphicon-chevron-right"></span>',
        twistieExpandedTpl: '<span class="glyphicon glyphicon-chevron-down"></span>',
        twistieLeafTpl: '&#9679;'
    });

}]);