$(document).ready(function(){
    $("#addLicenseForm").submit(function(event){
        event.preventDefault();

        var formData = {
            "license_name": $("#license_name").val(),
            "csrf_token": $("#csrf_token").val()
        };

        $.ajax({
            type: "POST",
            url: "/add_user_license",
            data: JSON.stringify(formData),
            contentType: "application/json",
            dataType: "json",
            success: function(response, textStatus, xhr) {
                $("#response").text(response.message);
            },
            error: function(error){
                $("#response").text(error.responseJSON.message);
            }
        });
    });
});