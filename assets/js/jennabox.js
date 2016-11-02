(function() {
   var global = this;

   var sort_uniq = function(coll, sort_f) {
      return _.uniq(_.sortBy(coll, sort_f));
   };

   $(document).ready(function() {
      $('[data-markdown]').each(function(idx, element) {
         $(element).html(markdown.toHTML($(element).data('markdown')));
      });

      $('[data-textarea-content]').each(function(idx, element) {
         $(element).val($(element).data('textarea-content'));
      });
   });
   
   angular.module('JennaBox', [])
      .controller('ChangePasswordController', function() {
         // pass 
      })
      .controller('ImageController', function($scope, $location) {
         angular.extend($scope, {
            tags: [],
            
            init: function() {
               if ($('#init_tag_list').length) {
                  $scope.tags = JSON.parse($('#init_tag_list').val());
               }

               $scope.summary = $('#summary_text').val();
            },

            getTagClasses: function(tag) {
               return ['badge', 'tag'];
            },

            deleteTag: function(tag) {
               $scope.tags = _.filter($scope.tags, function(t) { return t !== tag; });
            },

            addTagsFromInput: function(tag_input) {
               $scope.tags = sort_uniq(_.concat($scope.tags, tag_input.trim())).filter(function(x) {
                  return x.trim() !== '';
               });
            }
         });

         $scope.$watch('tag_input', function(tag_input) {
            if (tag_input && tag_input.endsWith(' ')) {
               $scope.addTagsFromInput(tag_input);
               $scope.tag_input = '';
            }
         });

         $scope.$watch('summary', function(summary) {
            $('#summary_display').html(markdown.toHTML(summary));
         });
      });

	interact('#upload-preview')
		.draggable({
			onmove: window.dragMoveListener
		})
		.resizable({
			preserveAspectRatio: true,
			edges: { right: true, bottom: true }
		})
		.on('resizemove', function (event) {
			var target = event.target,
				x = (parseFloat(target.getAttribute('data-x')) || 0),
				y = (parseFloat(target.getAttribute('data-y')) || 0);

			// update the element's style
			target.style.width  = event.rect.width + 'px';
			target.style.height = event.rect.height + 'px';

			target.setAttribute('data-x', x);
			target.setAttribute('data-y', y);
		});
})();
