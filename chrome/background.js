

function getImageClickHandler() {
  return function(info, tab) {
    // TODO
  };
};

function getSelectedTextHandler() {
  return function(info, tab) {
    var query = {"text": info.selectionText}
    var url = "verify.html?" + $.param( query )
    chrome.windows.create({ url: url, width: 400, height: 300, type: "popup" });
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
