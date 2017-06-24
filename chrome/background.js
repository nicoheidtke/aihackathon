

function getImageClickHandler() {
  return function(info, tab) {
    var query = {"image": info.srcUrl, "pageUrl": info.frameUrl ? info.frameUrl : info.pageUrl};
    var url = "verify.html?" + $.param( query );
    chrome.windows.create({ url: url, width: 600, height: 400, type: "popup" });
  };
};

function getSelectedTextHandler() {
  return function(info, tab) {
    var query = {"text": info.selectionText, "pageUrl": info.pageUrl};
    var url = "verify.html?" + $.param( query );
    chrome.windows.create({ url: url, width: 600, height: 400, type: "popup" });
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
