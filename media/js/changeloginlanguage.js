jQuery(document).ready(function() {

    var lang_choices = ['pt','fr','en'];

    function otherDivs(langdiv, langpref) {
        for (var i = 0; i < lang_choices.length; i++) {
            if (lang_choices[i] !== langpref) {
                jQuery(langdiv + lang_choices[i]).css('display', 'none');
            }
        }
    }

    jQuery('.switch-lang').on('click', function(evt) {
        var langpref = evt.currentTarget.dataset.lang;
        var langdiv = '#lang-';
        otherDivs(langdiv, langpref);
        var req_div = langdiv + langpref;
        jQuery(req_div).css('display', 'block');
    });
});
