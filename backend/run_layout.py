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
    roundify(nameToNodeInfo)
    normalize(nameToNodeInfo)

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

    proportion = 1 # the fraction of the layout's original size that it currently is
    byXCoord = sorted(nodeDict.items(), key=lambda kv: kv[1]['x'])

    for (_, prevInfo), (n, info) in zip(byXCoord, byXCoord[1:]):
        before = info['x']
        info['x'] *= proportion

        if info['x'] - prevInfo['x'] > proportion * maxGap:
            info['x'] = prevInfo['x'] + proportion * maxGap

        if before:
            after = info['x']
            proportion = after / before

    proportion = 1
    byYCoord = sorted(nodeDict.items(), key=lambda kv: kv[1]['y'])

    for (_, prevInfo), (n, info) in zip(byYCoord, byYCoord[1:]):
        before = info['y']
        info['y'] *= proportion

        if info['y'] - prevInfo['y'] > proportion * maxGap:
            info['y'] = prevInfo['y'] + proportion * maxGap

        if before:
            after = info['y']
            proportion = after / before

import random
def roundify(nodeDict):
    for info in nodeDict.values():
        x = 2 * info['x'] - 1
        y = 2 * info['y'] - 1
        if math.sqrt(x*x + y*y) > 1:
            if random.choice([True, False]):
                x = math.copysign(math.sqrt(1 - y*y), x)
            else:
                y = math.copysign(math.sqrt(1 - x*x), y)
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
            'cluster' : nodesJson[node]['cluster'],
        }

    with open('test_data/%s_clus_viz.json' % graphID, 'r') as f:
      with open('../docs/cluster_colors.json', 'w') as to:
          to.write(f.read())

    with open('../docs/nodes.json'.format(graphID), 'w') as f:
      f.write(json.dumps(output))

    # with open('test_data/%s_nodes_viz.json' % graphID, 'w') as f:
    #     f.write(json.dumps(output))

if __name__ == '__main__':
    graphID = int(sys.argv[1])
    algorithm = sys.argv[2]
    print("Running layout algorithm...")
    coords = runLayout(graphID, algorithm)
    print("Saving coordinates...")
    writeLayout(coords, graphID)
    # os.system('jython generate_image.py %s' % graphID)
