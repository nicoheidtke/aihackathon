
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

function verifySuccess(data) {
    $("#score_text").text(data.data.credibility.toFixed(2));
    if (data.credibility < 0.3) {
        $("#score_text").toggleClass("label-default label-danger");
    } else if (data.credibility < 0.5) {
        $("#score_text").toggleClass("label-default label-warning");
    } else if (data.credibility < 0.7) {
        $("#score_text").toggleClass("label-default label-info");
    } else {
        $("#score_text").toggleClass("label-default label-success");
    }
    $("#score_image").text("n/a");
    $("#status_message").text("Verification results are in!");
    $("#status_alert").toggleClass("alert-info alert-success");
};

function verifyFail(status, msg) {
    $("#score_text").text("error");
    $("#score_image").text("error");
    $("#status_message").text("Verification processs failed!");
    $("#error_message").text(status + ": " + JSON.stringify(msg));
    $("#status_alert").toggleClass("alert-info alert-danger");
};

function verify(query) {
     $.ajax({
        url:"http://54.72.165.0:8080/process_text", 
        method: "POST",
        data: JSON.stringify(query),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: verifySuccess,
    })
    .done(function() {})
    .fail(function(jqXHR, exception) {
        verifyFail(jqXHR.status, jqXHR.statusText);
    })
    .always(function() {});
};

function on_dom_loaded(event) {
    var pageUrl = getUrlParameter("pageUrl");
    var query = {"pageUrl": pageUrl} 
    var text = getUrlParameter("text");
    var image = getUrlParameter("image");
    if (text != null) {
        query["text"] = text
    }
    if (image != null) {
        image["text"] = image
    }
    verify(query);
};


document.addEventListener("DOMContentLoaded", on_dom_loaded);