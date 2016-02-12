'use strict';

var app = angular.module('ppApp', ['ngMaterial', 'firebase', 'ui.router', 'leaflet-directive'])
    
    .constant('Settings', {'api': "http://testing.aisleplus.com/api"})
    
    .config(function($mdThemingProvider, $stateProvider, $urlRouterProvider) {
        
        $mdThemingProvider.theme('default').primaryPalette('cyan').accentPalette('red');
        
        var templatesDir = "src/templates";
        
        $stateProvider
        
        .state('app', {
            url : "/",
            templateUrl : templatesDir + "/layout.html",
            cache : false
        })
        
        .state('search', {
            url : "search",
            cache : false,
            parent: "app",
            views: {
                "content": {
                    templateUrl : templatesDir + "/search.html",
                    controller: "SearchCtrl"
                }
            }
        })
        
        .state('map', {
            url : "map",
            cache : false,
            parent: "app",
            views: {
                "content": {
                    templateUrl : templatesDir + "/map.html",
                    controller: "MapCtrl"
                }
            }
        });
        
        $urlRouterProvider.otherwise("/map");
        
    })
    
    .run(function($rootScope, $state, $window, $templateCache, $mdSidenav, $mdUtil, $log) {
        
        $rootScope.isLoggedIn = $rootScope.user == null ? false : true;
        
        $rootScope.$on('$viewContentLoaded', function() {
            $templateCache.removeAll();
        });
   
        $rootScope.$state = $state;
        
        $rootScope.toggleLeft = buildToggler('left');
        
        function buildToggler(navID) {
            var debounceFn = $mdUtil.debounce(function() {
                $mdSidenav(navID).toggle().then(function() {
                    $log.debug("toggle " + navID + " is done");
                });
            }, 200);
    
            return debounceFn;
        };   
    });
    