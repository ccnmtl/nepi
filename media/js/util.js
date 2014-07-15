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

jQuery(document).ready(function () {
    jQuery("body").delegate('a.disabled', 'click', function()
    {
	    return false;  // call preventDefault and stopPropagation by default
	});
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
