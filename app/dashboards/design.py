import sys
import select
from dashboard.abstract.full import FullDash
from visual.design import DesignVisual
from utility.connector.connector import can_connect
from utility.connector.connector import connect


class DesignDash(FullDash):
    def __init__(self, name, server, model, is_multiple):
        super().__init__(DesignVisual(model,is_multiple), name,
                         server, "/design/")

    def load_graph(self, filenames):
        final_filenames = []
        for filename in filenames:
            if can_connect(filename):
                print(f"""We have found external data we could pull into your design ({filename}) to improve visualisation. 
                Would you like us to integrate this before proceding? (Y/N)""")
                i, o, e = select.select([sys.stdin], [], [], 10)
                if (i):
                    r = sys.stdin.readline().strip().lower()
                    if r == "y" or "yes":
                        print("Pulling Data.")
                        final_filenames.append(connect(filename))
                else:
                    final_filenames.append(filename)
                    print("Timeout, not integrating.")
            else:
                final_filenames.append(filename)   
        self.visualiser._load_graph(final_filenames)
        return super()._load_graph()
