/**
 * @param {array} $list - The list of elements to save. Expected to be an
 * array of jQuery elements, e.g. $('#answers li').
 *
 * @param {string} url - The url to POST to.
 *
 * @param {string} urlopt - String to prepend to the url option
 */
quizblock.saveOrder = function($list, url, urlopt) {
    var me = this;
    var worktodo = 0;

    url += '?';
    $list.each(function(index, element) {
        worktodo = 1;
        var id = $(element).attr('id').split('-')[1];
        url += urlopt + index + '=' + id + ';';
    });

    if (worktodo === 1) {
        quizblock.$.ajax({
            type: 'POST',
            url: url,
            beforeSend: function(xhr) {
                var token = $('meta[name="csrf-token"]').attr('content');
                xhr.setRequestHeader('X-CSRFToken', token);
            }
        });
    }
};
