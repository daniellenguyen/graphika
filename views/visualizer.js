// Draws all nodes in the given JSON file

// Defines the dimensions of the visualization

var width = $(window).width(),
    height = $(window).height();

// this is an svg container.
// holds the visualization.
var svg = d3.select('body')
            .append('svg')
            .attr('width', width)
            .attr('height', height);

    svg.append("rect")
       .attr("width", "100%")
       .attr("height", "100%")
       .attr("fill", "black");

d3.json("nodes.json", function(error1, graph) {
  d3.json("cluster_colors.json", function(error2, cluster_colors) {
    
    if (error1) throw error1;
    if (error2) throw error2;

    // prop is the name of the twitter acct. 
    // prop is dynamic and we only know it at runtime.
    for (var prop in graph) {
      var node = graph[prop];
      var cx = node.x;
      var cy = node.y;     
      var r  = node.default_size;
      var color = d3.color("#" + cluster_colors[node.cluster].color);

      svg.append("circle")
           .attr("cx", (width / 2) + (cx * 2500))
           .attr("cy", (height / 2) + (cy * -1) * 2500)
           .attr("r", 17 * r)
           .attr("fill", color)
           .attr("stroke", "black");
     }

  })

})