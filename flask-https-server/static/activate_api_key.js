$(document).ready(function(){
    $("#activateAPIKey").submit(function(event){
        event.preventDefault();

        var formData = {
            "csrf_token": $("#csrf_token").val(),
            "api_key": $("#api_key").val(),
            "lan_ip_address": "test",
            "remote_ip_address": "test",
            "node_port": "test",
            "public_key": "test"
        };

        $.ajax({
            type: "POST",
            url: "/activate_api_key",
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