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

    numNodes = len(edgesDict)

    for nodeID, _ in edgesDict.iteritems():
        graph.addNode(graphModel.factory().newNode(nodeID))

    for sourceID, targets in edgesDict.iteritems(): 
        sourceNode = graph.getNode(sourceID)
        for targetID in targets:
            targetNode = graph.getNode(targetID)
            graph.addEdge(graphModel.factory().newEdge(sourceNode, targetNode))

    # turn off edges and make background black
    PreviewController.getModel().getProperties().putValue("edge.show", False)
    PreviewController.getModel().getProperties().putValue("background-color", java.awt.Color.BLACK)

    graph = GraphController.getModel().getGraph()
    setNodePos(graph, nodeDict)
    setNodeColor(graph, nodeDict, clusterDict)
    setNodeSize(graph, numNodes)

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
# idk how this function works, I mostly just copypasted it from pygephi_layout.py
def setNodeSize(graph, numNodes):
    split_table = [(7000,20),(15000,200)]
    min_size = 0
    cur_smallest_dif_to_split_table_point = 100000
    for s in split_table:
        if abs(numNodes - s[0]) < cur_smallest_dif_to_split_table_point:
            cur_smallest_dif_to_split_table_point = abs(numNodes - s[0])
            min_size = s[1]

    # set node size to log indegree * min_size
    for node in graph.getNodes():
        node.getNodeData().setSize(math.sqrt(graph.getInDegree(node) + 1) * min_size * 0.1) # avoid problem with 0 sizes

def saveToFile(fileName):
    exporter = ExportController.getExporter('png')
    ExportController.exportFile(java.io.File(fileName), exporter)


if __name__ == '__main__':
    print 'Generating image...'
    ProjectController.newProject()
    graphID = sys.argv[1]
    buildGraph(graphID)
    saveToFile('%s_viz.png' % graphID)