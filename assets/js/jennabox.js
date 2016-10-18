(function() {
   angular.module('JennaBox', [])
      .controller('ChangePasswordController', function() {
         // pass 
      })
      .controller('ImageTagController', function($http, $location) {
         var self = this;
         this.loading = false;

         this.init = function() {
            self.tags = [];

            var query = $location.search();
            if ('id' in query || 'query' in query) {
               self.loading = true;
               $http.get('/image_tags', query)
                  .success(function(tags) {
                     self.tags = tags;
                     self.loading = false;
                  });
            }
         };

         this.getTagStyles = function(tag) {
            return {};
         };
      });
})();
