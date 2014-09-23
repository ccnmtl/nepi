jQuery(document).ready(function () {
    
    function resetSchoolChoice() {
        jQuery("div.user-profile-form select[name='school']").find('option').not('.all-or-none-option').remove();
        jQuery("div.user-profile-form input[name='profile_type']").removeAttr('checked');
    }
    
    function disableFacultyAccess() {
        jQuery("div.user-profile-form input[name='profile_type']").attr('disabled', 'disabled');
        jQuery("div.user-profile-form .faculty-access").addClass('disabled')
    }

    function enableFacultyAccess() {
        jQuery("div.user-profile-form input[name='profile_type']").removeAttr('disabled');
        jQuery("div.user-profile-form .faculty-access").removeClass('disabled')
    }

    function profileSchoolChoices(countryName) {
        jQuery.ajax({
            type: 'GET',
            url: '/schools/' + countryName + '/',
            dataType: 'json',
            error: function () {
                // This country does not exist in the database
                disableFacultyAccess();
            },
            success: function (json, textStatus, xhr) {
                if (json['schools'].length < 1) {
                    // There are no schools for this country
                    disableFacultyAccess();
                } else {
                    for (var i=0; i < json.schools.length; i++) {
                        var school = json.schools[i];
                        var option = "<option value='"  + school.id + "'>" + school.name + "</option>";
                        jQuery("div.user-profile-form select[name='school']").append(option)
                    }
        
                    if (currentSchoolId) {
                        jQuery("div.user-profile-form select[name='school']").val(currentSchoolId);
                        currentSchoolId = undefined;
                    }
                    enableFacultyAccess();          
                }
            }
        });
    }

    jQuery("div.user-profile-form select[name='country']").change(function() {
        var countryName = jQuery("div.user-profile-form select[name='country']").val();
        if (currentCountryName !== countryName) {
            currentCountryName = countryName;
            resetSchoolChoice();
            profileSchoolChoices(countryName);
        }
    });
    
    var currentSchoolId = jQuery("div.user-profile-form div.control-group.school").data('school-id');
    var currentCountryName = jQuery("div.user-profile-form select[name='country']").val();
    if (currentCountryName !== undefined && currentCountryName !== '-----') {
        profileSchoolChoices(currentCountryName);
    }
});
