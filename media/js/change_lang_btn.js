jQuery(document).ready(function() {
	
    jQuery('.chng-lang').click(function() {
    	
    	var langchoice = .
    	
    	var sitestr = location.origin;
    	var currentpath = location.pathname;
    	var rmlang = currentpath.substring(4)
        

        jQuery.getJSON('/captcha/refresh/', {}, function(json) {
            jQuery(form).find('input[name="captcha_0"]').val(json.key);
            jQuery(form).find('img.captcha').attr('src', json.image_url);
        });

        return false;
    });
});
