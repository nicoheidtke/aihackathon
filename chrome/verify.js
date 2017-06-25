var truthinessClass = {
    0: "alert-danger",
    1: "alert-warning",
    2: "alert-info",
    3: "alert-success"
};

var truthinessArray = [0.5, 0.7, 0.9];

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

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function verifyImageSuccess(data) {
    var trusted_url = data.trusted_source_url;
    if (trusted_url) {
        $("#status_message").html('<a href="' + trusted_url + '">Click here for a trusted source for this image!</a>');
        $("#status_alert").toggleClass("alert-info alert-success");
    } else {
        $("#status_message").text("This image was not found on trusted sources!");
        $("#status_alert").toggleClass("alert-info alert-warning");
    }
}

function verifyTextSuccess(data) {
    var scores = data.data;

    var site_cred = scores.site_credibility;
    if (site_cred <= 0) {
        $("#site_alert").show();
    }

    var credibility = scores.credibility.toFixed(2);
    if (credibility <= 0) {
        $("#status_message").text("Truthiness calculation has insufficient data");
        $("#status_alert").toggleClass("alert-info alert-default");
        $("#score_truthiness").text("not available");
        return;
    }

    $("#panel_score").show();
    $("#status_message").hide()
    $("#status_alert").hide();
    $("#score_truthiness").text(Math.round(credibility*100) + " %");
    var truthiness = 0;
    for (truthiness = 0; truthiness < truthinessArray.length; truthiness++) {
        if (truthinessArray[truthiness] > credibility)
            break;
    }
    
    var cls = truthinessClass[truthiness];
    $("#score_truthiness").toggleClass("label-default " + cls);

    var shares = scores.shares;
    if (shares >= 0) {
        $("#panel_shares").show()
        $("#score_shares").text(shares);
    }
    var engaged = scores.engaged;
    if (shares >= 0) {
        $("#panel_engaged").show()
        $("#score_engaged").text(engaged);
    }
};

function verifyFail(status, msg) {
    $("#score_truthiness").text("error");
    $("#status_message").text("Truthiness calculation failed!");
    $("#error_message").text(status + ": " + JSON.stringify(msg));
    $("#status_alert").toggleClass("alert-info alert-danger");
};

function verify_text(query) {
     $.ajax({
        url:"http://54.72.165.0:8080/process_text", 
        method: "POST",
        data: JSON.stringify(query),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: verifyTextSuccess,
    })
    .done(function() {})
    .fail(function(jqXHR, exception) {
        verifyFail(jqXHR.status, jqXHR.statusText);
    })
    .always(function() {});
};

function verify_image(query) {
     $.ajax({
        url:"http://54.72.165.0:8080/process_image", 
        method: "POST",
        data: JSON.stringify(query),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: verifyImageSuccess,
    })
    .done(function() {})
    .fail(function(jqXHR, exception) {
        verifyFail(jqXHR.status, jqXHR.statusText);
    })
    .always(function() {});
};

function on_dom_loaded(event) {
    $("#closeButton").click( function(){ self.close(); } );
    var pageUrl = atob(getUrlParameter("pageUrl"));
     $("#page_url").text(pageUrl);
    var query = {"pageUrl": pageUrl} 
    var text = getUrlParameter("text");
    var image = getUrlParameter("image");
    if (text != null) {
        text = atob(text);
        query["text"] = text;
        $("#source_item").text(text);
        verify_text(query);
    } else if (image != null) {
        image = decodeURIComponent(escape(atob(image)));
        query["imageUrl"] = image;
        $("#source_item").text(image);
        $("#source_img").attr("src",image);
        $("#source_img").show();
        verify_image(query);
    }
};


document.addEventListener("DOMContentLoaded", on_dom_loaded);

