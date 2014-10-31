(function() {
    
    Participant = Backbone.Model.extend({
        url: '/dashboard/people/filter/'
    });
    
    ParticipantCollection = Backbone.Collection.extend({
        urlRoot: '/dashboard/people/filter/',
        model: Participant,
        offset: 0,
        limit: 40,
        context: function () {
            var context = {'participants': this.toJSON(), 'page': 1};
            
            context.offset = this.offset;
            context.total = this.total;
            context.limit = this.limit;
            
            context.pages = Math.ceil(this.total / this.limit);
            
            context.first = this.offset + 1;
            context.last = this.offset + Math.min(this.limit, this.count);
            
            if (this.limit > 0) {
                context.page = (this.offset / this.limit) + 1;
            }

            if (this.hasOwnProperty('country')) {
                context.country = this.country;
            } else {
                context.country = '';
            }
            
            return context;
        },
        parse: function(response) {
            this.total = response.total;
            this.offset = response.offset;
            this.limit = response.limit;
            this.count = response.count;
            return response.participants;
        },
        refresh: function() {
            this.fetch({
                data: {page_size: this.limit},
                processData: true,
                reset: true
            });
        },
        set_page: function(page_no) {
            this.offset = (page_no - 1) * this.limit;
        },
        url: function() {
            var url = this.urlRoot + '?offset=' + this.offset;
            if (this.hasOwnProperty('country')) {
                url += "&country=" + this.country;
            }
            if (this.hasOwnProperty('role')) {
                url += "&role=" + this.role;
            }
            if (this.hasOwnProperty('school')) {
                url += "&school=" + this.school;
            }
            return url;
        }
    });
    
    window.PeopleView = Backbone.View.extend({
        events: {
            'click a.page-link': 'onTurnPage',
            'click #participant-search-button': 'onSearchParticipants',
            'click #participant-clear-button': 'onClearParticipantSearch',
            'change select[name="country"]': 'onCountryChange'
        },
        initialize: function(options) {
            _.bindAll(this,
                      'render',
                      'onClearParticipantSearch',
                      'onSearchParticipants',
                      'onTurnPage');

            var html = jQuery("#people-template").html();
            this.template = _.template(html);
            this.el_participants = options.el_participants;
            
            this.participants = new ParticipantCollection();
            this.participants.max_sessions = options.max_sessions;
            this.participants.on("reset", this.render);
            
            this.participants.refresh();
        },
        render: function() {
            var ctx = this.participants.context();
            
            jQuery(this.el_participants).html(this.template(ctx));
            
            if (this.participants.length > 0) {
                jQuery(".administration").show();
            } else {
                jQuery(".administration").hide();
            }
            
            jQuery("#participant-search-button").button();
            jQuery("#participant-clear-button").button();
        },
        onClearParticipantSearch: function(evt) {
            evt.preventDefault();
            jQuery(".help-block").hide();
            jQuery("select[name='role']").val('all');
            jQuery("select[name='country']").val('all');
            jQuery("select[name='school']").val('all');
            this.participants.page = 1;
            delete this.participants.role;
            delete this.participants.country;
            delete this.participants.school;
            this.participants.refresh();
            return false;
        },
        onSearchParticipants: function(evt) {
            var self = this;
            evt.preventDefault();
            
            this.participants.role = jQuery("select[name='role']").val();
            this.participants.country = jQuery("select[name='country']").val();
            this.participants.school = jQuery("select[name='school']").val();
             
            this.participants.page = 1;
            this.participants.refresh();
            
            return false;
        },
        clearSchoolChoices: function() {
            jQuery(this.el).find("select[name='school']").find('option').not('.unaffiliated').not('.all').remove();
        },
        onCountryChange: function(evt) {
            this.clearSchoolChoices();
            var countryId = jQuery("select[name='country']").val();
            
            jQuery.ajax({
                type: 'GET',
                url: '/schools/' + countryId + '/',
                dataType: 'json',
                error: function () {
                    // This country does not exist in the database
                },
                success: function (json, textStatus, xhr) {
                    var eltSchoolSelect = jQuery("select[name='school']")[0];
                    if (json.schools.length > 0) {
                        for (var i=0; i < json.schools.length; i++) {
                            var school = json.schools[i];
                            var option = "<option value='"  + school.id + "'>" + school.name + "</option>";
                            jQuery(eltSchoolSelect).append(option);
                        }
                    }
                }
            });
        },
        getParameterByName: function(name, url) {
            name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
            var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
                results = regex.exec(url);
            return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
        },        
        onTurnPage: function(evt) {
            evt.preventDefault();
            
            // parse the page number out of the url
            var href = jQuery(evt.currentTarget).attr("href");
            var page = this.getParameterByName("page", href);
            if (page !== null) {
                this.participants.set_page(parseInt(page, 10));
                this.participants.refresh();
            }
            return false;
        }
    });
})();