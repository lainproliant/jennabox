(function() {
   var global = this;
   
   var preview_image = function(input, img) {
      var reader = new FileReader();
      reader.onload = function(e) {
         img.attr('src', e.target.result);
         $('button:submit').prop('disabled', false);
      };
      reader.readAsDataURL(input.files[0]);
   };

   $(document).ready(function() {
      $('input:file').change(function() {
         preview_image(this, $('#upload-preview'));
      });
   });

})();
