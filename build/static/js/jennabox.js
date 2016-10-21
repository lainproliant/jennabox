(function() {
   var sort_uniq = function(coll, sort_f) {
      return _.sortedUniq(_.sortBy(coll, sort_f));
   };

   angular.module('JennaBox', [])
      .controller('ChangePasswordController', function() {
         // pass 
      })
      .controller('ImageTagController', function($scope, $location) {
         angular.extend($scope, {
            tags: [],
            tag_input_list: null,
            deleteTag: function(tag) {
               $scope.tags = _.filter($scope.tags, function(t) { t !== tag; });
            }
         });

         $scope.$watch('tag_input', function(tag_input) {
            if (tag_input && tag_input.endsWith(' ')) {
               var tag = tag_input.trim();
               if ($scope.tags.indexOf(tag) == -1) {
                  $scope.tags = sort_uniq(_.concat($scope.tags, tag));
                  $scope.tag_input = '';
               }
            }
         });
      });
})();
