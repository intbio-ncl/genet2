import build_util as bu
import warnings
warnings.filterwarnings("ignore")
from entities.abstract_entity import *
from entities.reaction import *
from entities.genetic import *
from entities.protein import *
from entities.chemical import *
from entities.interaction import *

def produce_ontology_graph():
    graph = bu.produce_ontology(__name__)
    graph.serialize("nv_design.xml",format="pretty-xml")

if __name__ == "__main__":
    produce_ontology_graph()