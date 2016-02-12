'use strict';
var app = angular.module('ppApp');

app.controller('MapCtrl', function($scope, $log, $timeout, $http, Settings) {

    /* commodity search */
    $scope.simulateQuery = false;
    $scope.isDisabled = true;
    $scope.querySearch = querySearch;
    $scope.selectedItemChange = selectedItemChange;
    $scope.searchTextChange = searchTextChange;
    
    $scope.center = {
        lat: 24.67,
        lng: 77.2,
        zoom: 4
    };

    function querySearch(query) {
        return query ? $scope.commodities.filter(createFilterFor(query)) : $scope.commodities;
    }

    function searchTextChange(text) {
        $log.info('Text changed to ' + text);
    }

    function selectedItemChange(item) {
        $scope.selected_commodity = item;
        $log.info('Item changed to ' + JSON.stringify(item));
        $timeout(function() {
            $scope.isDisabled = true;
            $scope.query();
        }, 500);
        
        //$scope.query();
    }

    function loadCommodities() {
        var url = Settings.api + "/distinct_commodities";
        $scope.commodities = [];
        $http.get(url).then(function(results) {
            var commodities = results.data.commodities;
            for (var i = 0; i < commodities.length; i++) {
                var c = commodities[i];
                $scope.commodities.push({
                    value : c.toLowerCase(),
                    display : c
                });
            }
            $scope.isDisabled = false;
        });
    }

    function createFilterFor(query) {
        var lowercaseQuery = angular.lowercase(query);
        return function filterFn(c) {
            return (c.value.indexOf(lowercaseQuery) === 0);
        };
    }

    loadCommodities();
    
    /** MAP results */
    var geojsonMarkerOptions = {
        radius : 5,
        fillColor : '#ff7800',
        color : '#000',
        weight : 1,
        opacity : 1,
        fillOpacity : 0.8
    };
            
    $scope.query = function() {
        $scope.where = {
            "commodity" : $scope.selected_commodity.display
        };
        $http({
            "url" : Settings.api + "/mandiprice",
            "params" : {
                "format" : "geojson",
                "where" : $scope.where
            }
        }).then(function(resp) {
            var geojson = resp.data["_items"];
            geojson.name = "Mandi Prices";
            geojson.keyField = "modal_price";
            $scope.mandiprice = {
                "data" : geojson,
                pointToLayer : function(feature, latlng) {
                    var marker = L.circleMarker(latlng, geojsonMarkerOptions);
                    marker.on('click', function() {
                       $scope.selected_mandiprice = marker.feature.properties;
                       console.log(marker.feature);
                    });
                    return marker;
                }
            };
            console.log(resp);
            $scope.isDisabled = false;
            
        }, function(err) {
            $scope.mandiprice = null;
        });
    }
});

app.controller('LeftCtrl', function($scope, $timeout, $mdSidenav, $log) {
    $scope.close = function() {
        $mdSidenav('left').close().then(function() {
            $log.debug("close LEFT is done");
        });
    };
});

app.controller('SearchCtrl', function($timeout, $q, $log, $http, $scope, Settings) {
    
});
