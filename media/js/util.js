function showVideo(radioElt) {
    if (jQuery("div.multiple-video-quiz").length > 0) {    
        // hide any videos that are currently playing
        // stop the video?
        jQuery("div.quiz-video").addClass("answer-video").removeClass("quiz-video");
        var video = jQuery(radioElt).siblings("div.answer-video")[0];
        
        jQuery(video).addClass("quiz-video");
        
        // center the video vertically 
        var top = jQuery("div.multiple-video-quiz").offset().top;
        var height = jQuery("div.multiple-video-quiz").outerHeight();
        
        var center = (top + height) / 2 - jQuery(video).height() / 2 ; 
        
        jQuery(video).css({"top": center + "px"});
        
        jQuery(video).removeClass("answer-video");
    }
}

jQuery(document).ready(function() {
    var a = jQuery("div.multiple-video-quiz").find("input[type='radio']:checked");
    if (a.length > 0) {
        showVideo(a[0]);
    }
    
    if (jQuery("div.survey").length > 0) {
        jQuery("div.block input[type='text']").addClass("optional");
    }
    
    if (jQuery("div.survey").length > 0 &&
            jQuery("input[name='submitted']").length > 0) {
        jQuery("div.block input[type='radio']").attr("disabled", "disabled");
    }
});


function is_form_complete(form) {
    var complete = true;
    
    var children = jQuery(form).find("input,textarea,select");
    jQuery.each(children, function() {
        if (complete && jQuery(this).is(":visible") &&
                !jQuery(this).hasClass("optional")) {
            
            if (this.tagName === 'INPUT' && this.type === 'text' ||
                this.tagName === 'TEXTAREA') {
                complete = jQuery(this).val().trim().length > 0;
            }
    
            if (this.tagName === 'SELECT') {
                var value = jQuery(this).val();
                complete = value !== undefined && value.length > 0 &&
                    jQuery(this).val().trim() !== '-----';
            }
    
            if (this.type === 'checkbox' || this.type === 'radio') {
                // one in the group needs to be checked
                var selector = 'input[name=' + jQuery(this).attr("name") + ']';
                complete = jQuery(selector).is(":checked");
            }
        }
    });
    return complete;
}

