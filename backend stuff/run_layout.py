import os
import json
from tulip import tlp

'''
input: (graphID : Int), (algorithm : String)
output: Dict (NodeName -> (X, Y))

algorithm options:
	"FM^3 (OGDF)"
	"Fast Multipole Embedder (OGDF)"
	"Fast Multipole Multilevel Embedder (OGDF)"
	"GRIP"
	"Pivot MDS (OGDF)"
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
def runLayout(graphID, algorithm, **extraParams):
	with open('test_data/%s_links.json' % graphID) as f:
		linksJson = json.loads(f.read())

	g = tlp.newGraph()
	nameToNode = { node : g.addNode() for node in linksJson.keys() }

	for source, targets in linksJson.items():
		for target in targets:
			g.addEdge(nameToNode[source], nameToNode[target])

	layout = g.getLayoutProperty('viewLayout')
	params = tlp.getDefaultPluginParameters(algorithm, g)
	params.update(extraParams)
	
	successful, errorMsg = g.applyLayoutAlgorithm(algorithm, layout, params)

	if not successful:
		raise Exception(errorMsg)

	maxX, maxY = 0, 0
	nameToCoords = {}

	for nodeName in linksJson.keys():
		x, y, z = layout[nameToNode[nodeName]]
		nameToCoords[nodeName] = x, y
		maxX = max(x, maxX)
		maxY = max(y, maxY)

	for node, (x, y) in nameToCoords.items():
		nameToCoords[node] = x / maxX, y / maxY

	return nameToCoords


def writeLayout(coords, graphID):
	with open('test_data/%s_links.json' % graphID) as f:
		linksJson = json.loads(f.read())

	with open('test_data/%s_nodes_viz.json' % graphID) as f:
		nodesJson = json.loads(f.read())

	output = {}
	for node, (x, y) in coords.items():
		output[node] = {
			'x' : x,
			'y' : y,
			'cluster' : nodesJson[node]['cluster'],
			'default_size' : nodesJson[node]['default_size'],
		}

	with open('test_data/%s_nodes_viz.json' % graphID, 'w') as f:
		f.write(json.dumps(output))


if __name__ == '__main__':
	graphID = int(sys.argv[1])
	algorithm = sys.argv[2]
	print("Running layout algorithm...")
	coords = runLayout(graphID, algorithm)
	print("Saving coordinates...")
	writeLayout(coords, graphID)
	os.system('jython generate_image.py %s' % graphID)
