document.addEventListener('DOMContentLoaded', function(){
   var refreshDiv = document.getElementById('refresh');
   if(refreshDiv){
      refreshDiv.addEventListener('DOMSubtreeModified', function () {
         location.reload();
      });
   }
});



