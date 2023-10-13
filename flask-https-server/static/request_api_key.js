$(document).ready(function(){
    $("#requestAPIKey").submit(function(event){
        event.preventDefault();

        var formData = {
            "license_name": $("#license_name").val(),
            "csrf_token": $("#csrf_token").val()
        };

        $.ajax({
            type: "POST",
            url: "/request_api_key",
            data: JSON.stringify(formData),
            contentType: "application/json",
            dataType: "json",
            success: function(response, textStatus, xhr) {
                $("#response").text(response.message);
                $("#api_key").text(response.api_key);
                $("#api_key_hash").text(response.api_key_hash);
            },
            error: function(error){
                $("#response").text(error.responseJSON.message);
            }
        });
    });
});