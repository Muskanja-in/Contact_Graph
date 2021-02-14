from pyvis.network import Network
from .graph import *

def fullgraphplot(time_lower,time_upper):
    """ 
    Function print the overall node graph within the selected time window. 
  
    Require two table named identity and activity to retrive the data. 
  
    Parameters: 
    time_lower (datetime): Lower time limit
    time_upper (datetime): Upper time limit
  
    Returns: 
    None: Currently only prints, make changes in the last line to return value 
  
    """

    edges_list,node_list,title_list = graphformation(time_lower,time_upper)
    node_size = []
    for i in range(len(node_list)):
        node_size.append(5)
    g = Network(
            height="750px",
            width="100%",
            bgcolor="#222222",
            font_color="white")
    g.add_nodes(node_list,label=node_list,title=title_list, size= node_size)
    g.add_edges(edges_list)
    g.show("nx.html")
    return
