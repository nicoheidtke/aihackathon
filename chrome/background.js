

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
  "title" : "Image truthiness",
  "type" : "normal",
  "contexts" : ["image"],
  "onclick" : getImageClickHandler()
});

chrome.contextMenus.create({
  "title" : "Text truthiness",
  "type" : "normal",
  "contexts" : ["selection"],
  "onclick" : getSelectedTextHandler()
});
