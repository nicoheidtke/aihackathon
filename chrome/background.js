

function getImageClickHandler() {
  return function(info, tab) {
    var query = {"image": btoa(info.srcUrl), "pageUrl": btoa(info.frameUrl ? info.frameUrl : info.pageUrl)};
    var url = "verify.html?" + $.param( query );
    chrome.windows.create({ url: url, width: 600, height: 400, type: "popup" });
  };
};

function getSelectedTextHandler() {
  return function(info, tab) {
    var query = {"text": btoa(unescape(encodeURIComponent(info.selectionText))), "pageUrl": btoa(info.pageUrl)};
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
