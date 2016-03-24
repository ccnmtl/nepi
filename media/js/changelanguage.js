jQuery(document).ready(function() {

    var lang_choices = ['pt','fr','en'];

    function langInPath() {
        for (i = 0; i < lang_choices.length; i++) {
            if (window.location.pathname.indexOf(lang_choices[i]) >= 0) {
                return true;
            }
        }
        return false;
    }
    jQuery('.switch-lang').on('click', function(evt) {
        var langpref = evt.currentTarget.dataset.lang;
        var domainstr = window.location.origin;
        var path = window.location.pathname;
        var newpath = '';
        /* check if there is a language prefix in path, allows
         * for furture language choices to be added */
        if (langInPath()) {
            path = window.location.pathname.split('/')[2];
            newpath = '/' + langpref + '/' + path + '/';
        } else {
            newpath = '/' + langpref +  path;
        }
        window.location.href = newpath;
    });
});
