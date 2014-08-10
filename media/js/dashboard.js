 jQuery(document).ready(function () {
     
     // handle hash tag navigation
     var hash = window.location.hash;
     hash && jQuery('.dashboard-nav a[href="' + hash + '"]').tab('show');
     
     // when the nav item is selected update the page hash
     jQuery('.dashboard-nav a').on('shown', function (e) {
         window.location.hash = e.target.hash;
         scrollTo(0,0);
     })
     
     // initialize date pickers for create & edit group
     jQuery(".datepicker").datepicker({dateFormat: "mm/dd/yy"});
     jQuery(".calendar").click(function() {
         jQuery(this).prev().datepicker("show"); 
     });
     
     function showError(elt) {
        jQuery(elt).parents('.control-group').addClass('error');
     }
     
     // Join Group Functionality
     function clearSchoolGroupChoices(elt) {
         jQuery(elt).find("div.schoolgroup table").find('tr.content-row').remove();
     }

     function clearSchoolChoices(elt) {
         jQuery(elt).find("select[name='school']").find('option').remove();
     }

     function populateSchoolChoices(elt, eltCountrySelect, eltSchoolSelect, callback) {
        clearSchoolChoices(elt);
        
        var countryName = jQuery(eltCountrySelect).val();
        
        jQuery.ajax({
            type: 'GET',
            url: '/schools/' + countryName + '/',
            dataType: 'json',
            error: function () {
                // This country does not exist in the database
                showError(eltCountrySelect);
            },
            success: function (json, textStatus, xhr) {
                if (json['schools'].length < 2) {
                    // There are no schools for this country
                    showError(eltCountrySelect);
                } else {
                    for (var i=0; i < json.schools.length; i++) {
                        var school = json.schools[i];
                        var option = "<option value='"  + school.id + "'>" + school.name + "</option>";
                        jQuery(eltSchoolSelect).append(option)
                    }
                    jQuery(eltSchoolSelect).parents(".control-group").removeClass('error');
                    jQuery(eltSchoolSelect).parents(".control-group").fadeIn();
                    if (callback) {
                        callback();
                    }
                }
            }
        });
    }

    function populateSchoolGroupChoices(elt, eltSchoolSelect, eltGroupTable) {
        clearSchoolGroupChoices(eltGroupTable);
        
        var schoolId = jQuery(eltSchoolSelect).val();
        
        jQuery.ajax({
            type: 'GET',
            url: '/groups/' + schoolId + '/',
            dataType: 'json',
            error: function () {
                // This school does not exist in the database. Unlikely.
                showError(eltSchoolSelect);
            },
            success: function (json, textStatus, xhr) {
                if (json['groups'].length < 1) {
                    // There are no groups for this country
                    showError(eltSchoolSelect);
                } else {
                    // @todo - a client-side template would do nicely here
                    for (var i=0; i < json.groups.length; i++) {
                        var group = json.groups[i];
                        var row = "<tr class='content-row'>" + 
                            "<td>" + group.name + "</td>" + 
                            "<td>" + group.start_date + "</td>" +
                            "<td>" + group.end_date + "</td>" +
                            "<td>" + group.creator + "</td>";
                        if (group.member) {
                            row += "<td>Joined</td>";
                        } else {
                            row += "<td><form action='/join_group/' method='post'>" +
                            "<button class='btn btn-primary btn-small'>Join</button>" + 
                            "<input type='hidden' name='group' value='" + group.id + "'></input>" +
                            "</form></td>";
                        }
                        row += "</tr>";
                        jQuery(eltGroupTable).append(row);
                    }
                    jQuery(eltGroupTable).parents(".control-group").removeClass('error');
                    jQuery(eltGroupTable).parents(".control-group").fadeIn();
                }
            }
        });
    }

    jQuery("#user-groups select[name='country']").change(function() {
        var elt = jQuery(this).parents('div.modal')[0];
        
        clearSchoolGroupChoices(elt);
        clearSchoolChoices(elt);
        jQuery(elt).find("div.control-group.school").fadeOut();
        jQuery(elt).find("div.control-group.schoolgroup").fadeOut();
        
        var eltSchoolChoice = jQuery(elt).find("select[name='school']")[0];
        populateSchoolChoices(elt, this, eltSchoolChoice);
    });

    jQuery("#find-a-group").find("select[name='school']").change(function() {
        var elt = jQuery(this).parents('div.modal')[0];
        var eltGroupChoice = jQuery(elt).find("div.schoolgroup table")[0];
        populateSchoolGroupChoices(elt, this, eltGroupChoice);
    });
    
    jQuery('#find-a-group').on('show', function () {
        clearSchoolGroupChoices(this);
        clearSchoolChoices(this);
        jQuery(this).find("div.control-group").removeClass('error');
        jQuery(this).find("select[name='country']").val('-----');
        jQuery(this).find("div.control-group.school").hide();
        jQuery(this).find("div.control-group.schoolgroup").hide();
    });
    
    jQuery("button.leave-group").on("click", function() {
        if (confirm("Are you sure you want to leave this group?")) {
            var row = jQuery(this).parents('tr')[0];
            var table = jQuery(row).parents('table')[0];
    
            var frm = jQuery(this).parent('form')[0];
            jQuery.ajax({
                url: frm.action,
                data: jQuery(frm).serialize(),
                type: "POST",
                success: function (data) {
                    if (jQuery(table).find('tr.content-row').length == 1) {
                        jQuery(".your-groups").fadeOut(function() {
                            jQuery(row).remove();
                        });
                    } else {
                        jQuery(row).fadeOut(function() {
                            jQuery(row).remove();
                        });
                    }
                },
                error: function(data)  {
                    alert("An error occurred. Please try again");
                }
            });
        }
        return false;
    });
    
    jQuery("button.delete-group").on("click", function() {
        if (confirm("Are you sure you want to delete this group?")) {
            var row = jQuery(this).parents('tr')[0];
            var table = jQuery(row).parents('table')[0];
    
            var frm = jQuery(this).parent('form')[0];
            jQuery.ajax({
                url: frm.action,
                data: jQuery(frm).serialize(),
                type: "POST",
                success: function (data) {
                    if (jQuery(table).find('tr.content-row').length == 1) {
                        jQuery(".your-groups-created").fadeOut(function() {
                            jQuery(row).remove();
                        });
                    } else {
                        jQuery(row).fadeOut(function() {
                            jQuery(row).remove();
                        });
                    }
                },
                error: function(data)  {
                    alert("An error occurred. Please try again");
                }
            });
        }
        return false;
    });
    
    jQuery("button.archive-group").on("click", function() {
        if (confirm("Are you sure you want to archive this group?")) {
            var row = jQuery(this).parents('tr')[0];
            var table = jQuery(row).parents('table')[0];
    
            var frm = jQuery(this).parent('form')[0];
            jQuery.ajax({
                url: frm.action,
                data: jQuery(frm).serialize(),
                type: "POST",
                success: function (data) {
                    if (jQuery(table).find('tr.content-row').length == 1) {
                        jQuery(".your-groups-created").fadeOut(function() {
                            jQuery(row).remove();
                        });
                    } else {
                        jQuery(row).fadeOut(function() {
                            jQuery(row).remove();
                        });
                    }
                },
                error: function(data)  {
                    alert("An error occurred. Please try again");
                }
            });
        }
        return false;
    });

    jQuery('#create-a-group').on('show', function () {
        jQuery(this).find("div.control-group").removeClass("error");
        
        var countryElt = jQuery(this).find("select[name='country']")[0];
        var schoolElt = jQuery(this).find("select[name='school']")[0];
        if (jQuery(countryElt).attr('disabled') === undefined) {
            // country is enabled -- icap member. clear country + school
            jQuery(countryElt).val('-----');
            jQuery(schoolElt).find('option').remove();
            jQuery(this).find("div.control-group.school").hide();
        } else if (jQuery(schoolElt).attr('disabled') === undefined) {
            // country is disabled & school is enabled -- country admin
            // clear the school choice
            jQuery(schoolElt).val('-----');
        }
        jQuery(this).find("input[name='name']").val('');
        jQuery(this).find(".date").datepicker('setValue', '');
    });
    
    jQuery('button.edit-group-button').click(function () {
        var pk = jQuery(this).data('pk');
        var name = jQuery(this).data('name');
        var startdate = jQuery(this).data('start-date');
        var enddate = jQuery(this).data('end-date');
        
        var modal = jQuery("#edit-a-group");
        jQuery(modal).find("input[name='pk']").val(pk);
        jQuery(modal).find("input[name='name']").val(name);
        jQuery(modal).find("input[name='start_date']").datepicker('setDate', startdate);
        jQuery(modal).find("input[name='end_date']").datepicker('setDate', enddate);
        jQuery(modal).modal();
    });

    jQuery('form.create-group, form.edit-group').submit(function(evt) {
        jQuery(this).find("div.control-group").removeClass("error");

        var name = this.name.value.trim();
        var startdate = new Date(this.start_date.value.trim());
        var enddate = new Date(this.end_date.value.trim());
        
        var submit = true;

        if ('country' in this && this.country.value === '-----') {
            jQuery(this).find("div.control-group.country").addClass("error");
            submit = false;
        }
        
        if ('school' in this && this.school.value === '-----') {
            jQuery(this).find("div.control-group.school").addClass("error");
            submit = false;
        }

        if (name === '') {
            jQuery(this).find("div.control-group.name").addClass("error");
            submit = false;
        }
        
        
        if (startdate == 'Invalid Date') {
            jQuery(this).find("div.control-group.start_date").addClass("error");
            submit = false;
        }

        if (enddate == 'Invalid Date') {
            jQuery(this).find("div.control-group.end_date").addClass("error");
            submit = false;
        }
        
        if (startdate > enddate) {
            jQuery(this).find("div.control-group.start_date").addClass("error");
            jQuery(this).find("div.control-group.end_date").addClass("error");
            submit = false;
        }
       
        return submit;
    });
    
    function updateFacultyAccess(msg, url, elt) {
        if (confirm(msg)) {
            var row = jQuery(elt).parents('tr')[0];
            var table = jQuery(row).parents('table')[0];
    
            jQuery.ajax({
                url: url,
                data: {'user_id': jQuery(elt).data('user-id')},
                type: "POST",
                success: function (data) {
                    jQuery(row).fadeOut(function() {
                        jQuery(row).remove();
                    });
                },
                error: function(data)  {
                    alert("An error occurred. Please try again");
                }
            });
        }        
    }
    
    jQuery("button.deny-faculty-access").on("click", function() {
        var msg = "Are you sure you want to deny faculty access?";
        var url = '/faculty/deny/';
        return updateFacultyAccess(msg, url, this);
    });

    jQuery("button.confirm-faculty-access").on("click", function() {
        var msg = "Are you sure you want to grant faculty access?";
        var url = '/faculty/confirm/';
        return updateFacultyAccess(msg, url, this);
    });
    
    // Create group initialization
    // select the user's country for picking groups
    if (profile_attributes.role == 'faculty' || profile_attributes.role == 'country') {
        var eltCountrySelect =  jQuery("#create-a-group").find("select[name='country']");
        var eltSchoolSelect =  jQuery("#create-a-group").find("select[name='school']");
        
        jQuery(eltCountrySelect).val(profile_attributes.country);
        jQuery(eltCountrySelect).attr('disabled', 'disabled');
        
        populateSchoolChoices(jQuery("#create-a-group"),
            eltCountrySelect, eltSchoolSelect,
            function() {
                if (profile_attributes.role == 'faculty') {
                    jQuery(eltSchoolSelect).val(profile_attributes.school);
                    jQuery(eltSchoolSelect).attr('disabled', 'disabled');
                }
            });
    }
 });
    