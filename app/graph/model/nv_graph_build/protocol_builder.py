import warnings
warnings.filterwarnings("ignore")

import build_util as bu
from entities.abstract_entity import *
from entities.container import *
from entities.apparatus import *
from entities.instrument import *
from entities.protocol import *
from entities.action import *

def produce_ontology_graph():
    graph = bu.produce_ontology(__name__)
    graph.serialize("nv_protocol.xml",format="pretty-xml")

if __name__ == "__main__":
    produce_ontology_graph()