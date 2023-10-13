$(document).ready(function(){
    $("#registrationForm").submit(function(event){
        event.preventDefault();
        var formData = {
            "username": $("#username").val(),
            "password": $("#password").val(),
            "invitation_code": $("#invite").val(),
            //'g-recaptcha-response': $("#g-recaptcha-response").val()
        };

        $.ajax({
            type: "POST",
            url: "/register",
            data: JSON.stringify(formData),
            contentType: "application/json",
            dataType: "json",
            success: function(response, textStatus, xhr) {
                //if (xhr.status == 200) {
                //    window.location.href = "/login";
                //} else {
                $("#response").text(response.message);
                //}
            },
            error: function(error){
                $("#response").text(error.responseJSON.message);
            }
        })


    });
});