(function () {
    'use strict';
    angular.module('ng-file-model', [])
    .directive("ngFileModel", ['$parse', function ($parse) {
        return {
            restrict: 'A',
            link: function (scope, element, attributes) {

                var model = $parse(attributes.ngFileModel);
                var isMultiple = attributes.multiple;
                var modelSetter = model.assign;

                element.bind('change', function () {
                    var values = [];
                    angular.forEach(element[0].files, function (item) {
                        var reader = new FileReader();
                        reader.readAsDataURL(item);
                        reader.onload = function (loadEvent) {
                            scope.$apply(function () {
                                var value = {
                                    url: URL.createObjectURL(item),
                                    lastModified: item.lastModified,
                                    lastModifiedDate: item.lastModifiedDate,
                                    name: item.name,
                                    size: item.size,
                                    type: item.type,
                                    data: loadEvent.target.result
                                }

                                values.push(value);

                                if (isMultiple) {
                                    modelSetter(scope, values);
                                } else {
                                    modelSetter(scope, values[0]);
                                }
                            });
                        };
                    });
                    /*scope.$apply(function () {
                        if (isMultiple) {
                            modelSetter(scope, values);
                        } else {
                            modelSetter(scope, values[0]);
                        }
                    });*/
                });


                /*scope.ngFileModel = [];

                element.bind("change", function (changeEvent) {
                    var reader = new FileReader();
                    reader.onload = function (loadEvent) {
                        scope.$apply(function () {

                            console.log(changeEvent);
                            console.log(loadEvent);

                            scope.ngFileModel = {
                                lastModified: changeEvent.target.files[0].lastModified,
                                lastModifiedDate: changeEvent.target.files[0].lastModifiedDate,
                                name: changeEvent.target.files[0].name,
                                size: changeEvent.target.files[0].size,
                                type: changeEvent.target.files[0].type,
                                data: loadEvent.target.result
                            };
                        });
                    }

                    angular.forEach(changeEvent.target.files, function(targetFile){
                        reader.readAsDataURL(targetFile);
                    });

                });*/
            }
        }
    }]);
})();