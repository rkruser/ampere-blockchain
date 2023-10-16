$(document).ready(function(){
    $("#registrationForm").submit(function(event){
        event.preventDefault();
        var formData = {
            "temp_id": $("#temp_id").val(),
            "code": $("#code").val(),
        };

        $.ajax({
            type: "POST",
            url: "/complete-registration/finalize",
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