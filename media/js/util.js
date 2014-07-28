function showAnswer(questionId) {
    var qid = "#q" + questionId;
    var display_type = jQuery(qid).css("display");
    jQuery(qid).css("display", "block");
}

function is_form_complete(form) {
    var complete = true;

    var children = jQuery(form).find("input,textarea,select");
    jQuery.each(children, function() {
        if (complete && jQuery(this).is(":visible")) {

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

function validate_numeric_input(evt) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    key = String.fromCharCode( key );
    var regex = /[0-9]|\./;
    if( !regex.test(key) ) {
      theEvent.returnValue = false;
      if(theEvent.preventDefault) theEvent.preventDefault();
    }
}

jQuery(document).ready(function () {
    jQuery("body").delegate('a.disabled', 'click', function() {
	    return false;  // call preventDefault and stopPropagation by default
	});
    jQuery("body").delegate('.toggle-primary-toc', 'click', function() {
        jQuery('.slide-out-menu').toggleClass('open');
    });
    jQuery("body").delegate('.slide-out-menu a', 'click', function() {
        jQuery('.slide-out-menu').toggleClass('open');
        window.location = jQuery(this).attr(href);
    });
    jQuery("body").delegate("div.pageblock.numeric-only input[type='text']",
            'keypress', validate_numeric_input);
    jQuery("form").submit(function(evt) {
        if (!is_form_complete(this)) {
            evt.stopImmediatePropagation();
            alert("Please complete all form fields before continuing.");
            return false;
        } else {
            return true;
        }
    });
});
