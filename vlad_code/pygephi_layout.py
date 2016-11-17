#/usr/local/bin/jython
import math, java
import os, glob, sys, time
import classpath
path = os.path.realpath(__file__)
toolkit = os.path.join(os.path.dirname(path), 'gephi-toolkit.jar')

classpath.addFile(toolkit)
# TODO: need /Users/jason/Code/gephi/toolkit/gephi-toolkit/org-openide-util.jar?

# necessary for save - there should be a less scattershot way to do this?
#for j in glob.glob('/Users/jason/Code/gephi/platform/platform/modules/*.jar'): classpath.addFile(j)

#faster json
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/jyson-1.0.2.jar")
from com.xhaus.jyson import JysonCodec as json

sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/org-openide-util-lookup-8.3.1.jar")
import org.openide.util.Lookup as Lookup
Lookup = Lookup.getDefault().lookup

def lookup(name, namespace='org.gephi.'):
    return Lookup(java.lang.Class.forName(namespace + name))


ProjectController = lookup('project.api.ProjectController')
ExportController = lookup('io.exporter.api.ExportController')
# GraphController = lookup('graph.api.GraphController')
RankingController = lookup('ranking.api.RankingController')
PreviewController = lookup('preview.api.PreviewController')
PreviewProperty = lookup('preview.api.PreviewProperty')
ImportController = lookup('io.importer.api.ImportController')
GraphController = lookup('graph.api.GraphController')

class GephiVisualizer(object):
    
    def __init__(self, layout_options_file_name):
        ProjectController.newProject()
        self.workspace = ProjectController.getCurrentWorkspace()
        self.graph_source = None
        self.base_file_name = ""
        self.output_file_type = "png"
        self.default_layout_type = "fruchterman"
        layout_options_file = open(layout_options_file_name,'r')
        self.layout_path = "/".join(layout_options_file_name.split("/")[:-1])
        self.layout_options = json.loads(layout_options_file.read())
        layout_options_file.close()
        self.base_output_file_name = self.layout_options["name"]
        self.published_map_id = int(self.layout_options["published_map_id"])
        self.fruchterman_total_steps = [650] #500
        self.fruchterman_grav = [100] #x*.1 for x in [0..10]
        self.fruchterman_speed = [20] #[0..20]
        self.fa_total_steps = [50] #[500..600]
        self.fa_grav = [200] #100
        self.fa_attraction_strength = [8] #[0..20]
        self.fa_repulsion_strength = 2000
        self.max_usual_network_size = 15000
        
    def getGraphFromClustermap(self):
        self.graph_source = "clustermap"

        #create graph model
        graph_model = GraphController.getModel()
        graph = graph_model.getGraph()
        
        #connect to dbs for graph data
        print("getting json data at: ", time.time())
        clumap_id_file = open("%s/%d_links.json" % (self.layout_path, self.published_map_id),"r")
        clumap_str = clumap_id_file.read()
        self.clumap_nodearcs = json.loads(clumap_str)
        self.number_of_nodes = len(self.clumap_nodearcs)
        #update fruchterman params based on network size
        self.fruchterman_total_steps = [int(650*self.number_of_nodes/self.max_usual_network_size)] #500
        clumap_id_file.close()
        print("loading network at: ", time.time())
        #first load all the nodes
        print("loading nodes at: ", time.time())
        for node_arc_id, node_arc_metadata in self.clumap_nodearcs.iteritems():
            graph_node = graph_model.factory().newNode(node_arc_id)
            graph.addNode(graph_node)
        print("loading edges at: ", time.time())
        #now load the edges
        for node_arc_id, node_arc_metadata in self.clumap_nodearcs.iteritems(): 
            graph_node = graph.getNode(node_arc_id)
            
            # print("*" * 80)
            # print("node_arc_metadata: %s" % node_arc_metadata)

            for node_alt in node_arc_metadata:
                graph_node_alt = graph.getNode(node_alt)

                # print("node_alt: %s" % node_alt)
                # print("graph.getNode(node_alt): %s" % graph_node_alt)

                graph_edge = graph_model.factory().newEdge(graph_node, graph_node_alt)
                graph.addEdge(graph_edge)    
                
        #optionally, also get node metadata
        print("getting node metadata at: ", time.time())
        try: 
            clumap_node_meta_file = open("/%s/%d_node_meta.json" % (self.layout_path, self.published_map_id),"r")
            node_meta_str = clumap_node_meta_file.read()
            self.node_meta_hash = json.loads(node_meta_str)
            clumap_node_meta_file.close()
        except Exception as e:
            print("failed to get node metadata: ", e.message)
            self.node_meta_hash = {}
            
        #set node size
        self.setNodeSize()
        
    def setNodeSize(self):
        #Rank node size by in-degree
        '''
        ranking_model = RankingController.getModel()
        degree_ranking = ranking_model.getRanking("nodes","indegree")
        size_transformer = RankingController.getModel().getTransformer("nodes","renderable_size")
        split_table = [(7000,20),(15000,200)]
        min_size = 0
        cur_smallest_dif_to_split_table_point = 100000
        for s in split_table:
            if abs(self.number_of_nodes - s[0]) < cur_smallest_dif_to_split_table_point:
                cur_smallest_dif_to_split_table_point = abs(self.number_of_nodes - s[0])
                min_size = s[1]
        size_transformer.setMinSize(min_size)
        size_transformer.setMaxSize(min_size*20)
        RankingController.transform(degree_ranking,size_transformer)
        '''
        #try adjust_sizes model
        #identify min size
        split_table = [(7000,20),(15000,200)]
        min_size = 0
        cur_smallest_dif_to_split_table_point = 100000
        for s in split_table:
            if abs(self.number_of_nodes - s[0]) < cur_smallest_dif_to_split_table_point:
                cur_smallest_dif_to_split_table_point = abs(self.number_of_nodes - s[0])
                min_size = s[1]
        #get graph and model        
        graph_model = GraphController.getModel()
        graph = graph_model.getGraph()
        #get nodes
        nodes = list(graph.getNodes())                
        #set node size to log indegree * min_size
        for node in nodes:
            node_data = node.getNodeData()
            in_degree = graph.getInDegree(node)            
            node_data.setSize(math.sqrt(in_degree+1)*min_size*0.1) # avoid problem with 0 sizes
            # print "changed %s size from %s to %s" % (node_data.getLabel(), value, (1 + scale(value)))
        
    def layoutGraph(self):
        layout_type = self.layout_options["layout_params"]["layout_type"]
        layout_builder = None
        graph_layout = None
        # Setup Layout
        if layout_type == "fruchterman":
            layout_builder = lookup('layout.plugin.fruchterman.FruchtermanReingoldBuilder')
        elif layout_type == "force_atlas":
            layout_builder = lookup('layout.plugin.forceAtlas.ForceAtlas')
        elif layout_type == 'multi_level':
            layout_builder = lookup('layout.plugin.multilevel.YifanHuMultiLevel')
        #common steps
        graph_layout = layout_builder.buildLayout()
        #load graph model
        graph_model = GraphController.getModel()
        graph = graph_model.getGraph()
        num_nodes = graph.getNodeCount()
        graph_layout.setGraphModel(graph_model)
        graph_layout.resetPropertiesValues() # set defaults
        
        #turn off edges in preview
        preview_model = PreviewController.getModel()
        preview_model.getProperties().putValue("edge.show", False)
        
        #finalized coords file name for referencing back in the rest of mapperbot
        finalized_coords_file_name = ''
        
        #layout-specific steps:
        if layout_type == "fruchterman":
            graph_layout.area = 10000
            graph_layout.gravity = 0
            graph_layout.speed = 20
            for total_steps in self.fruchterman_total_steps:
                for grav_param in self.fruchterman_grav:
                    for speed_param in self.fruchterman_speed:
                        graph_layout.gravity = grav_param
                        graph_layout.speed = speed_param  
                        out_file_name = '%s/%s_fruchterman_%d_%d_%d.%s' % (self.layout_path, self.base_output_file_name, total_steps, int(grav_param*10), speed_param, self.output_file_type)
                        finalized_coords_file_name = "%s_%d_gephi_node_coords.json" \
                                                     %(out_file_name.rstrip(".%s" %(self.output_file_type)), self.published_map_id)
                        self.runLayout(graph_layout, layout_type, total_steps) 
                        self.rotateGraph()
                        self.setNodeSize()
                        self.saveCoords(out_file_name.rstrip(".%s" %(self.output_file_type)), graph)
                        self.saveToFile(out_file_name)                                                                   
        elif layout_type == "force_atlas":
            graph_layout.adjustSizes = False
            graph_layout.repulsionStrength = self.fa_repulsion_strength
            for total_steps in self.fa_total_steps:
                for grav_param in self.fa_grav:
                    for attraction_strength_param in self.fa_attraction_strength:
                        graph_layout.gravity = grav_param
                        graph_layout.attractionStrength = attraction_strength_param
                        out_file_name = '%s/%s_forceatlas_%d_%d_%d.%s' % (self.layout_path, self.base_output_file_name, total_steps, int(grav_param*10), attraction_strength_param, \
                                                                                                 self.output_file_type)
                        finalized_coords_file_name = "%s_%d_gephi_node_coords.json" \
                                                     %(out_file_name.rstrip(".%s" %(self.output_file_type)), self.published_map_id)
                        self.runLayout(graph_layout, layout_type, total_steps)
                        self.rotateGraph()   
                        self.saveCoords(out_file_name.rstrip(".%s" %(self.output_file_type)), graph)
                        self.saveToFile(out_file_name)
        elif layout_type == 'multi_level':
            total_steps = 10000
            out_file_name = '%s/%s_multilevel_%d.%s' % (self.layout_path, self.base_output_file_name, total_steps, self.output_file_type)
            self.runLayout(graph_layout, layout_type, total_steps)
            self.rotateGraph()
            self.saveCoords(out_file_name.rstrip(".%s" %(self.output_file_type)), graph)
            self.saveToFile(out_file_name)
        
        #store the finalized coords file name in a reference file
        coords_ref_file = open('%s/%d_coords_reference_file.txt' %(self.layout_path, self.published_map_id),'w')
        coords_ref_file.write(finalized_coords_file_name)
        coords_ref_file.close()
                        
    def rotateGraph(self):
        #rotate graph until the highest-power nodes on top 
        # Setup Layout
        layout_type = 'rotate'
        graph_layout_class = lookup('layout.plugin.rotate.ClockwiseRotate')
        graph_layout = graph_layout_class.buildLayout()
        #load graph model
        graph_model = GraphController.getModel()
        graph = graph_model.getGraph()
        graph_layout.setGraphModel(graph_model)
        graph_layout.resetPropertiesValues() # set defaults
        
        #turn off edges in preview
        preview_model = PreviewController.getModel()
        preview_model.getProperties().putValue("edge.show", False)
        
        #iteratively rotate layout by 45d and evaluate it
        #evaluation criteria: nodes with highest power should be on top
        graph_layout_quality_hash = {}
        for graph_angle in range(0, 360, 45):
            #rotate by 45d every time so we don't over-rotate
            graph_layout.angle = min(float(graph_angle), 45.0)
            total_steps = 100
            self.runLayout(graph_layout, layout_type, total_steps)
            graph_layout_quality_hash[self.evaluateRotation(graph)] = float(graph_angle)
            
        #identify optimum angle and rotate it once again 
        max_quality = max(graph_layout_quality_hash.keys())
        #rotate it by 45 one last time to return to 0
        print("optimal angle: ", graph_layout_quality_hash[max_quality])
        graph_layout.angle = 45.0+graph_layout_quality_hash[max_quality]
        total_steps = 100
        self.runLayout(graph_layout, layout_type, total_steps)
                                                                                            
                        
    def runLayout(self, graph_layout, layout_type, num_steps):
        graph_layout.initAlgo()
        print("running %s for %d steps at: %f" % (layout_type, num_steps, time.time()))
        while num_steps and graph_layout.canAlgo():
            if num_steps%100==0: print("steps: ", num_steps, " at time: ", time.time())
            graph_layout.goAlgo()
            num_steps -= 1
            
    def evaluateRotation(self, graph):
        total_power_y = 0
        for node in self.node_meta_hash:
            node_power = self.node_meta_hash[node]['power']
            node_obj = graph.getNode(node)
            if node_obj:
                node_data = node_obj.getNodeData()
                node_y = node_data.y()
                total_power_y += node_power*node_y
        return total_power_y
        
    def saveToFile(self, output_file_name):        
        graph_image_exporter = ExportController.getExporter(self.output_file_type)
        if self.output_file_type == "pdf": graph_image_exporter.landscape = True
        ExportController.exportFile(java.io.File(output_file_name), graph_image_exporter)
        
    def saveCoords(self, fname, graph):
        self.coords_file = open("%s_%d_gephi_node_coords.json" %(fname, self.published_map_id),'w')
        self.coords_hash = {}
        for node_arc_id, node_arc_metadata in self.clumap_nodearcs.items():
            gephi_n_obj = graph.getNode(node_arc_id)
            if gephi_n_obj:
                gephi_n = gephi_n_obj.getNodeData()
                self.coords_hash[node_arc_id] = {'coords':[gephi_n.x(), gephi_n.y(), gephi_n.z(), gephi_n.getSize()]}
            else:
                self.coords_hash[node_arc_id] = {'coords':[0, 0, 0, 0]}
        self.coords_hash_str = json.dumps(self.coords_hash)
        self.coords_file.write(self.coords_hash_str)
        self.coords_file.close()
        
if __name__ == '__main__':
    gephi_viz = GephiVisualizer(sys.argv[1])
    gephi_viz.getGraphFromClustermap()
    gephi_viz.layoutGraph()
    #gephi_viz.layoutGraph("force_atlas") 
