from app.dashboards.abstract_dashboard.full import FullDash
from app.dashboards.visual.design import DesignVisual


class DesignDash(FullDash):
    def __init__(self, name, server, graph):
        super().__init__(DesignVisual(graph), name,
                         server, "/design/")
