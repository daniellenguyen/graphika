#/usr/local/bin/jython
import math, java
import os, sys
import classpath

path = os.path.realpath(__file__)
toolkit = os.path.join(os.path.dirname(path), 'gephi-toolkit.jar')
classpath.addFile(toolkit)

# faster json
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/jyson-1.0.2.jar")
from com.xhaus.jyson import JysonCodec as json

sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/org-openide-util-lookup-8.3.1.jar")
import org.openide.util.Lookup as Lookup
Lookup = Lookup.getDefault().lookup
lookup = lambda name: Lookup(java.lang.Class.forName('org.gephi.%s' % name))
ProjectController = lookup('project.api.ProjectController')
ExportController = lookup('io.exporter.api.ExportController')
GraphController = lookup('graph.api.GraphController') 
PreviewController = lookup('preview.api.PreviewController')
PreviewProperty = lookup('preview.api.PreviewProperty')

# mutates GraphController and PreviewController
def buildGraph(graphID):
    graphModel = GraphController.getModel()
    graph = graphModel.getGraph()

    with open('test_data/%s_links.json' % graphID) as f:
        edgesDict = json.loads(f.read())

    with open('test_data/%s_nodes_viz.json' % graphID) as f:
        nodeDict = json.loads(f.read())

    with open('test_data/%s_clus_viz.json' % graphID) as f:
        clusterDict = json.loads(f.read())

    for nodeID in edgesDict.iterkeys():
        graph.addNode(graphModel.factory().newNode(nodeID))

    for sourceID, targets in edgesDict.iteritems(): 
        sourceNode = graph.getNode(sourceID)
        for targetID in targets:
            targetNode = graph.getNode(targetID)
            graph.addEdge(graphModel.factory().newEdge(sourceNode, targetNode))

    graphProperties = PreviewController.getModel().getProperties()
    graphProperties.putValue("edge.show", False) # turn off edges
    graphProperties.putValue("background-color", java.awt.Color.BLACK) # make background black

    graph = GraphController.getModel().getGraph()
    setNodePos(graph, nodeDict)
    setNodeColor(graph, nodeDict, clusterDict)
    setNodeSize(graph)

# mutates graph
def setNodePos(graph, nodeInfo):
    for node in graph.getNodes():
        node.getNodeData().setX(1000 * float(nodeInfo[str(node)]['x']))
        node.getNodeData().setY(1000 * float(nodeInfo[str(node)]['y']))

# mutates graph
def setNodeColor(graph, nodeInfo, clusterInfo):
    for node in graph.getNodes():
        cluster = nodeInfo[str(node)]['cluster']
        color = str(clusterInfo[str(cluster)]['color'])
        r = int(color[0:2], 16) / 255.0
        g = int(color[2:4], 16) / 255.0
        b = int(color[4:6], 16) / 255.0
        node.getNodeData().setColor(r, g, b)

# mutates graph
def setNodeSize(graph):
    numNodes = len(list(graph.getNodes()))
    splitTable = [(7000, 20), (15000, 200)]
    minSize = 0
    minDifToSplitTablePoint = 100000

    for a, b in splitTable:
        if abs(numNodes - a) < minDifToSplitTablePoint:
            minDifToSplitTablePoint = abs(numNodes - a)
            minSize = b

    # set node size to log indegree * min_size
    for node in graph.getNodes():
        node.getNodeData().setSize(math.sqrt(graph.getInDegree(node) + 1) * minSize * 0.1) # avoid problem with 0 sizes


def saveToFile(fileName):
    exporter = ExportController.getExporter('png')
    ExportController.exportFile(java.io.File(fileName), exporter)


if __name__ == '__main__':
    print 'Generating image...'
    ProjectController.newProject()
    graphID = sys.argv[1]
    buildGraph(graphID)
    saveToFile('%s_viz.png' % graphID)
