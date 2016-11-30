// Draws all nodes in the given JSON file

// Defines the dimensions of the visualization

var width = 2000,
    height = 2000;

// this is an svg container.
// holds the visualization.
var svg = d3.select('body')
            .append('svg')
            .attr('width', width)
            .attr('height', height);

d3.json("test1.json", function(error, graph) {
	if (error) throw error;

    // prop is the name of the twitter acct. 
    // prop is dynamic and we only know it at runtime.
    for (var prop in graph) {
    	var cx = graph[prop].coords[0];
    	var cy = graph[prop].coords[1];      
      var cz = graph[prop].coords[2]; 
    	var r  = graph[prop].coords[3];

    	svg.append("circle")
           .attr("cx", 1000 + cx)
           .attr("cy", 1000 + cy * -1)
           .attr("cz", cz)
    	     .attr("r", r)
           .attr("fill", "steelblue")
           .attr("stroke", "black");
    }

})