 jQuery(document).ready(function () {
     
     var hash = window.location.hash;
     hash && jQuery('.dashboard-nav a[href="' + hash + '"]').tab('show');
     
     // when the nav item is selected update the page hash
     jQuery('.dashboard-nav a').on('shown', function (e) {
         window.location.hash = e.target.hash;
         scrollTo(0,0);
     })

     function showError(elt) {
        jQuery(elt).parent().find("div.help-inline").fadeIn();
     }
     
     // Join Group Functionality
     function clearSchoolGroupChoices(elt) {
         jQuery(elt).find("div.schoolgroup table").find('tr.group-row').remove();
     }

     function clearSchoolChoices(elt) {
         jQuery(elt).find("select[name='school']").find('option').remove();
     }

     function populateSchoolChoices(elt, eltCountrySelect, eltSchoolSelect) {
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
                    jQuery("div.help-inline").hide();
                    jQuery(eltSchoolSelect).parents(".control-group").fadeIn();                      
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
                        var row = "<tr class='group-row'>" + 
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
                    jQuery("div.help-inline").hide();
                    jQuery(eltGroupTable).parents(".control-group").fadeIn();
                }
            }
        });
    }
    
    jQuery('button.find-groups').click(function() {
        jQuery("div.help-inline").fadeOut();
        var elt = jQuery(this).parents('.action-container')[0];
        clearSchoolGroupChoices(elt);
        clearSchoolChoices(elt);
        jQuery(elt).find("select[name='country']").val('-----');
        jQuery(elt).find("div.control-group.school").fadeOut();
        jQuery(elt).find("div.control-group.schoolgroup").fadeOut();
        jQuery(".find-group").fadeIn();
    });
    
    jQuery('button.hide-container').click(function(evt) {
        var elt = jQuery(this).parents('.action-container')[0];
        jQuery(elt).fadeOut();
        return false;
    });
    
    jQuery("select[name='country']").change(function() {
        var elt = jQuery(this).parents('.action-container')[0];
        
        clearSchoolGroupChoices(elt);
        clearSchoolChoices(elt);
        jQuery(elt).find("div.control-group.school").fadeOut();
        jQuery(elt).find("div.control-group.schoolgroup").fadeOut();
        
        var eltSchoolChoice = jQuery(elt).find("select[name='school']")[0];
        populateSchoolChoices(elt, this, eltSchoolChoice);
    });

    jQuery("select[name='school']").change(function() {
        var elt = jQuery(this).parents('.action-container')[0];
        var eltGroupChoice = jQuery(elt).find("div.schoolgroup table")[0];
        populateSchoolGroupChoices(elt, this, eltGroupChoice);
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
                    if (jQuery(table).find('tr.group-row').length == 1) {
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


    /**
    jQuery('#add_group_button').click(function() {
        jQuery('#add_group_div').load('/add_group/');
    });
    
    jQuery('#edit_group_button').click(function() {
        jQuery('#edit_group_div').load('/edit_group/');
    });
    
    var profilebtn = jQuery('#user-profile-button');
    profilebtn.click(function(){jQuery('#new_profile').load('/dashboard/update_profile/{{user_profile.pk}}/');});
    
    var onDelete = function()
    {
            jQuery.post(this.href, function(data)
            {   
                if (data.result == "ok")
                {
                    alert("Group deleted successfully");
                    location.reload();
                } else
                {
                    // handle error processed by server here
                    alert("smth goes wrong");
                }
            }).fail(function()
            {
                // handle unexpected error here
                alert("error");
            });
            return false;
    };//end of on delete

    jQuery(".delete_link").click(onDelete);
    **/
 });
    