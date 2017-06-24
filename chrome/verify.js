
function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

function textVerifySuccess(data) {
    $("#text_result").text("Result: " + JSON.stringify(data))
};

function textVerifyFail(data) {
    $("#text_result").text("Error: " + JSON.stringify(data))
};

function verify_text(text) {
    var query = { "text": text} 
     $.ajax({
        url:"http://54.72.165.0:8080/process_text", 
        method: "POST",
        data: JSON.stringify(query),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: textVerifySuccess,
    })
    .done(function() {})
    .fail(function(data) {
        textVerifyFail(data);
    })
    .always(function() {});
};

function on_dom_loaded(event) {
    var text = getUrlParameter("text");
    if (text != null) {
        verify_text(text);
    }
    var image = getUrlParameter("image");
    if (image != null) {
        //verify_image(text);
    }
};


document.addEventListener("DOMContentLoaded", on_dom_loaded);