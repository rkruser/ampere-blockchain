$(document).ready(function(){
    $("#registrationForm").submit(function(event){
        event.preventDefault();
        var formData = {
            "email": $("#email").val(),
            "username": $("#username").val(),
            "password": $("#password").val(),
            "invitation_code": $("#invite").val(),
            'g-recaptcha-response': $("#g-recaptcha-response").val()
        };

        $.ajax({
            type: "POST",
            url: "/register",
            data: JSON.stringify(formData),
            contentType: "application/json",
            dataType: "json",
            success: function(response) {
                if (response.redirect_url) {
                    window.location.href = response.redirect_url;  // Redirect the user
                } else if (response.message) {
                    $("#response").text(response.message);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $("#response").text(jqXHR.responseJSON.message || "An error occurred during registration.");
            }
        })
    });
});