angular.module('ERAS').factory('OntologyUtil', ['ArrayUtil', function(ArrayUtil) {

    var _getTree = function(ontologyTree, mode, removeRootNodesWithoutChildren, removeEmptySubnodes) {

        if(!mode){
            mode = 'entity';
        }
        
        var tree = [];
        var nodeMap = [];

        var addNode = function(parentKey, nodeKey, nodeValue){
            var node = {label: nodeKey, children: []};

            var relationsNode = {label: '[relations]', children: []};
            var childrenNode = {label: '[children]', children: []};

            if(mode == 'both'){
                node.children.push(relationsNode);
                node.children.push(childrenNode);
            }

            nodeMap[nodeKey] = {node: node, relationsBag: relationsNode, childrenBag: childrenNode};

            if (parentKey) {
                if (mode == 'both') {
                    nodeMap[parentKey].childrenBag.children.push(node);
                } else if (mode == 'entity') {
                    nodeMap[parentKey].node.children.push(node);
                }
                node.parent = nodeMap[parentKey].node;
            } else {
                tree.push(node);
            }

            if(mode == 'both' || mode == 'relation') {

                angular.forEach(Object.keys(nodeValue.relations).sort(), function (relationKey) {
                    var relationNode = {label: relationKey, children: []};

                    if(mode == 'both' ){
                        nodeMap[nodeKey].relationsBag.children.push(relationNode);
                    }else{
                        node.children.push(relationNode);
                    }

                    var ranges = nodeValue.relations[relationKey];

                    angular.forEach(ranges, function (range) {
                        relationNode.children.push({label: range, children: []});
                    });
                });
            }

            angular.forEach(Object.keys(nodeValue.children).sort(), function(childKey){
                if(mode == 'both' || mode == 'entity') {
                    addNode(nodeKey, childKey, nodeValue.children[childKey]);
                }else if(mode == 'relation'){
                    addNode(null, childKey, nodeValue.children[childKey]);
                }
            });
        };

        angular.forEach(Object.keys(ontologyTree).sort(), function(nodeKey){
            addNode(null, nodeKey, ontologyTree[nodeKey])
        });

        if(mode == 'both' && removeEmptySubnodes) {
            var removeEmptyNodes = function (node) {

                var nodesToRemove = [];
                angular.forEach(node.children, function (child) {
                    if (child.label == '[relations]' && child.children.length == 0) {
                        nodesToRemove.push(child);
                    } else if (child.label == '[children]') {
                        if (child.children.length == 0) {
                            nodesToRemove.push(child);
                        } else {
                            angular.forEach(child.children, function (grandchild) {
                                removeEmptyNodes(grandchild);
                            });
                        }
                    }
                });

                angular.forEach(nodesToRemove, function (nodeToRemove) {
                    ArrayUtil.remove(node.children, nodeToRemove);
                });
            };

            angular.forEach(tree, function (node) {
                removeEmptyNodes(node);
            });
        }

        if(removeRootNodesWithoutChildren) {

            var rootNodesToRemove = [];

            angular.forEach(tree, function (node) {
                if(node.children == 0){
                    rootNodesToRemove.push(node);
                }
            });

            angular.forEach(rootNodesToRemove, function (node) {
                ArrayUtil.remove(tree, node);
            });
        }

        return tree;
    };

    return {
        getTree : _getTree
    }

}]);
