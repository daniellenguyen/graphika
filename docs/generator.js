var fs = require('fs');
var page = require('webpage').create();
page.viewportSize = { width: 1280, height: 1024 }; // size of window
page.zoomFactor = 0.4;
var url = 'file://' + fs.absolute('./docs/index.html');

page.open(url, function(status) {
	setTimeout(function() {
		page.render('graph_render.png');
        phantom.exit();
	}, 2000);
    
});