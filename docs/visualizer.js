// Draws all nodes in the given JSON file

// Defines the dimensions of the visualization

var imageSize = Math.max($(window).width(), $(window).height());
var nodeToImageSize = 0.07

// this is an svg container.
// holds the visualization.
var svg = d3.select('body')
            .append('svg')
            .attr('width', imageSize)
            .attr('height', imageSize);

    svg.append("rect")
       .attr("width", "100%")
       .attr("height", "100%")
       .attr("fill", "black");

d3.json("nodes.json", function(error1, graph) {
  if (error1) throw error1;

  d3.json("cluster_colors.json", function(error2, cluster_colors) {
    if (error2) throw error2;

    //prop is the name of the twitter acct. 
    //prop is dynamic and we only know it at runtime.
    for (var prop in graph) {
      var node = graph[prop];
      var cx = node.x;
      var cy = node.y;
      var r  = node.radius;
      var color = d3.color("#" + cluster_colors[node.cluster].color);

     svg.append("circle")
           .attr("cx", cx * imageSize + 100)
           .attr("cy", cy * imageSize + 100)
           .attr("r",  r  * imageSize * nodeToImageSize)
           .attr("fill", color)
           .attr("stroke", "black");
     }

  })

})