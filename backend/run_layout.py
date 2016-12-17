import os
import json
import math
from tulip import tlp

'''
input: (graphID : Int), (algorithm : String)
output: Dict (NodeName -> (X, Y))

algorithm options:
    "FM^3 (OGDF)"
    "Fast Multipole Embedder (OGDF)"
    "Fast Multipole Multilevel Embedder (OGDF)"
    "Pivot MDS (OGDF)"
    "GRIP" (kind of slow for larger data sets)
    - (weird result) "Frutcherman Reingold (OGDF)"
    - (weird result) "GEM Frick (OGDF)"
    - (slow) "GEM (Frick)"
    - (slow) "Bertault (OGDF)"
    - (slow) "Kamada Kawai (OGDF)"
    - (slow) "LinLog"
    - (slow) "Upward Planarization (OGDF)"
    - (slow) "Visibility (OGDF)"
    - (InsufficientMemoryException) "Stress Majorization (OGDF)"
    - (Python stops working?) "Sugiyama (OGDF)"
'''
def runLayout(graphID, algorithm):
    with open('test_data/%s_links.json' % graphID) as f:
        linksJson = json.loads(f.read())

    g = tlp.newGraph()
    nameToNode = {}
    nodeToName = {}
    for name in linksJson.keys():
        node = g.addNode()
        nameToNode[name] = node
        nodeToName[node] = name

    for source, targets in linksJson.items():
        for target in targets:
            g.addEdge(nameToNode[source], nameToNode[target])

    layout = g.getLayoutProperty('viewLayout')
    params = tlp.getDefaultPluginParameters(algorithm, g)
    successful, errorMsg = g.applyLayoutAlgorithm(algorithm, layout, params)

    if not successful:
        raise Exception(errorMsg)

    # params = tlp.getDefaultPluginParameters('Fast Overlap Removal', g)
    # params['x border'] = 5
    # params['y border'] = 5
    # successful, errorMsg = g.applyLayoutAlgorithm('Fast Overlap Removal', layout, params)

    # if not successful:
    #     raise Exception(errorMsg)

    nameToNodeInfo = {}
    for name, node in nameToNode.items():
        x, y, z = layout[node]
        nameToNodeInfo[name] = {
            'x' : x,
            'y' : y,
            'name' : name,
        }

    calcSizes(nameToNodeInfo, nodeToName, g)
    normalize(nameToNodeInfo)
    reduceGaps(nameToNodeInfo)
    normalize(nameToNodeInfo)
    # roundify(nameToNodeInfo)
    # normalize(nameToNodeInfo)

    return nameToNodeInfo


def calcSizes(nameToNodeInfo, nodeToName, graph):
    maxSize = math.sqrt(tlp.maxDegree(graph) + 1)

    for node in graph.getNodes():
        name = nodeToName[node]
        nameToNodeInfo[name]['radius'] = math.sqrt(graph.deg(node) + 1) / maxSize


# make all coordinates lie within the range [0, 1]
def normalize(nodeDict):
    minX = min(info['x'] for info in nodeDict.values())
    minY = min(info['y'] for info in nodeDict.values())

    # make sure coordinates start at 0
    for info in nodeDict.values():
        info['x'] -= minX
        info['y'] -= minY

    maxX = max(info['x'] for info in nodeDict.values())
    maxY = max(info['y'] for info in nodeDict.values())

    # make sure coordinates go up to 1
    for info in nodeDict.values():
        info['x'] /= maxX
        info['y'] /= maxY


def reduceGaps(nodeDict):
    maxGap = 0.05

    totalDifference = 0
    byXCoord = sorted(nodeDict.values(), key=lambda info: info['x'])

    for prevInfo, info in zip(byXCoord, byXCoord[1:]):
        info['x'] -= totalDifference
        curGap = info['x'] - prevInfo['x']
        if curGap > maxGap:
            totalDifference += curGap - maxGap
            info['x'] = prevInfo['x'] + maxGap

    totalDifference = 0
    byYCoord = sorted(nodeDict.values(), key=lambda info: info['y'])

    for prevInfo, info in zip(byYCoord, byYCoord[1:]):
        info['y'] -= totalDifference
        curGap = info['y'] - prevInfo['y']
        if curGap > maxGap:
            totalDifference += curGap - maxGap
            info['y'] = prevInfo['y'] + maxGap


def roundify(nodeDict):
    for info in nodeDict.values():
        # scale values from [0, 1] to [-1, 1]
        x = 2 * info['x'] - 1
        y = 2 * info['y'] - 1

        # move values that are outside the circle to the edge of the circle
        if math.sqrt(x*x + y*y) > 1:
            if abs(y) > abs(x):
                x = math.copysign(math.sqrt(1 - y*y), x)
            else:
                y = math.copysign(math.sqrt(1 - x*x), y)

        # scale values back to [0, 1]
        info['x'] = (x + 1) / 2
        info['y'] = (y + 1) / 2


def writeLayout(nodeDict, graphID):
    with open('./test_data/%s_nodes_viz.json' % graphID) as f:
        nodesJson = json.loads(f.read())

    output = {}
    for node, info in nodeDict.items():
        output[node] = {
            'x' : info['x'],
            'y' : info['y'],
            'radius' : info['radius'],
            'cluster' : nodesJson[node]['cluster']
        }

    with open('test_data/%s_clus_viz.json' % graphID, 'r') as f:
      with open('../docs/cluster_colors.json', 'w') as to:
          to.write(f.read())

    with open('../docs/nodes.json'.format(graphID), 'w') as f:
      f.write(json.dumps(output))


if __name__ == '__main__':
    graphID = sys.argv[1]
    algorithm = sys.argv[2]
    print("Running layout algorithm...")
    coords = runLayout(graphID, algorithm)
    print("Saving coordinates...")
    writeLayout(coords, graphID)

