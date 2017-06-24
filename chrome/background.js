/*
chrome.browserAction.onClicked.addListener(function(tab) {
  chrome.tabs.sendRequest(tab.id, {method: "getSelection"}, function(response){
     sendServiceRequest(response.data);
  });
});

function sendServiceRequest(selectedText) {
  var serviceCall = 'http://www.google.com/search?q=' + selectedText;
  chrome.tabs.create({url: serviceCall});
}
*/

function getImageClickHandler() {
  return function(info, tab) {
    $.get( "https://httpbin.org/get", function( data ) {
        requestId = data["origin"]
        var url = 'imageVerify.html#' + requestId;
        chrome.windows.create({ url: url, width: 520, height: 660 });
    });
  };
};

function getSelectedTextHandler() {
  return function(info, tab) {
      $.get( "https://httpbin.org/get", function( data ) {
        requestId = data["origin"]
                console.info(data)
        chrome.windows.create({ url: "google.de", width: 520, height: 660 });
        var url = 'textVerify.html#' + requestId;
        chrome.windows.create({ url: url, width: 520, height: 660 });
      });
  };
};

chrome.contextMenus.create({
  "title" : "Verify image",
  "type" : "normal",
  "contexts" : ["image"],
  "onclick" : getImageClickHandler()
});

chrome.contextMenus.create({
  "title" : "Verify text",
  "type" : "normal",
  "contexts" : ["selection"],
  "onclick" : getSelectedTextHandler()
});