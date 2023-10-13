$(document).ready(function(){
    $("#loginForm").submit(function(event){
        event.preventDefault();

        var formData = {
            "username": $("#username").val(),
            "password": $("#password").val()
        };

        $.ajax({
            type: "POST",
            url: "/login",
            data: JSON.stringify(formData),
            contentType: "application/json",
            dataType: "json",
            success: function(response, textStatus, xhr) {
                if (xhr.status == 200) {
                    window.location.href = "/";
                } else {
                    $("#response").text(response.message);
                }
            },
            error: function(error){
                $("#response").text(error.responseJSON.message);
            }
        });
    });
});