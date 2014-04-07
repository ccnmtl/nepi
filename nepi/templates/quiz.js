jQuery( document ).ready(function() {
// should this be onload?
    if (checkStyleSheet(right-question.css)){alert("good style sheet found");};
    if (checkStyleSheet(bad-question.css)){alert("bad style sheet found");};


})



function checkStyleSheet(url){
   var found = false;
   for(var i = 0; i < document.styleSheets.length; i++){
      if(document.styleSheets[i].href==url){
          found=true;
          //break;
      }
   }
//   if(!found){
//       $('head').append(
//           $('<link rel="stylesheet" type="text/css" href="' + url + '" />')
//       );
//   }
    return found;
}



$('#casetitle').hide();

// ?
$('#casetitle').load(function(){
    
});

//we want the answer fields to appear when the user clicks on the question
$('#casequestion').click(function(){
    
});

      <div class="casesanswerdisplay">
        <a href="#q{{question.id}}" class="moretoggle">Show answer(s) &gt;&gt;</a>
        <div id="q{{question.id}}" class="toggleable">
          <p><i>The correct answer(s):</i></p>
