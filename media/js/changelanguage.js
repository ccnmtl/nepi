jQuery(document).ready(function() {
	console.log("loaded");

	jQuery('.switch-lang').on("click", function(evt) {	
		
		var langpref = evt.currentTarget.dataset.lang;
    	var domainstr = window.location.origin;
    	var path = window.location.pathname;
    	var newpath = ""
    	/*/about/ length is 7 so if length of path is longer
    	 * than that it has a language already indicated in
    	 * url and we need to remove it, /help/ with a language
    	 * prefix is also more than 7 for the pathname attribute */
    	if(window.location.pathname.length > 7)
    	{
    		path = window.location.pathname.split( '/' )[2];
    		newpath = "/" + langpref + "/" + path + "/";
    	}
    	else if(window.location.pathname.length <= 7)
    	{
    		newpath = "/" + langpref +  path;
    	}
    	
    	window.location.href = newpath;

    });
});