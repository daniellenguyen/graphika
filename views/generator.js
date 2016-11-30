var fs = require('fs');
var page = require('webpage').create();
page.viewportSize = { width: 75, height: 75 };
var url = 'file://' + fs.absolute('./views/index.html');

page.open(url, function(status) {
    page.render('graph_render.png');
  phantom.exit();
});