import os
from utility.summarise import get_all_views
from dashboard.abstract.abstract import AbstractDash
from visual.instance import InstanceVisual


button_class = "btn btn-light dash-toolbar"
graph_col_class = "col sub_graph"
text_col_class = "col accordian"
class ResultDash(AbstractDash):
    def __init__(self,name,server):
        super().__init__(name,server,"/full_graph/")
        self.visualiser = InstanceVisual()
        self._build_app()


    def _build_app(self):
        self.app.layout = self.create_div("container",[])[0]
        self.build()

    def load_graph(self,filename):
        '''
        Seems silly to load the graph for each function...
        '''
        self.visualiser = InstanceVisual(filename)
        download = os.path.basename(filename)
        name = download.split(".")[0]
        s_view,t_view,f_view = get_all_views(filename) 
        changelog = ""

        name_heading =  self.create_heading_1("title",name)
        top_bar_children = name_heading
        top_bar = self.create_div("top-bar",top_bar_children)

        back_button = self.create_button("Back","job_result",className=button_class)
        download = self.create_button("Download","download/" + download,className=button_class)
        visualiser = self.create_button("Visualiser","visualiser/" + name,className=button_class)
        buttons_children = back_button + download + visualiser
        button_row = self.create_div("buttons",buttons_children,className = "row")

        summary_title = self.create_heading_3("summary","Design Summary")
        summary_children = summary_title + self._build_accordian(s_view)
        summary_col = self.create_div("summary_col",summary_children,className=text_col_class)
        figure = self._create_figure(self.visualiser.set_component_preset)
        summary_fig_col = self.create_div("summary_fig_col",figure,className=graph_col_class)
        summary = self.create_div("summary_col",summary_col + summary_fig_col,className = "row")

        heirachy_title = self.create_heading_3("heirachy","Heirachy")
        heirachy_children = heirachy_title + self._build_accordian(t_view)
        heirachy_col = self.create_div("heirachy_row",heirachy_children,className=text_col_class)
        figure = self._create_figure(self.visualiser.set_heirarchy_preset)
        heirachy_fig_col = self.create_div("heirachy_fig_col",figure,className=graph_col_class)
        heirachy = self.create_div("heirachy_col",heirachy_col + heirachy_fig_col,className = "row")

        functional_title = self.create_heading_3("functional","Functional")
        functional_children = functional_title + self._build_accordian(f_view)
        functional_col = self.create_div("functional_row",functional_children,className=text_col_class)
        figure = self._create_figure(self.visualiser.set_interaction_preset)
        functional_fig_col = self.create_div("functional_fig_col",figure,className=graph_col_class)
        functional = self.create_div("functional_col",functional_col + functional_fig_col,className = "row")

        changelog_title = self.create_heading_3("changelog","Changelog")
        changelog_children = changelog_title
        changelog_col = self.create_div("changelog_row",changelog_children,className = "col")
        changelog = self.create_div("changelog_col",changelog_col,className = "row")

        layout = top_bar + button_row + summary + heirachy + functional + changelog
        
        self.children = self.create_div("container",layout)
        self.app.layout = self.create_div("container",self.children)[0]
        self.build()



    def _create_figure(self,graph_preset):
        graph_preset()
        figure_layout_elements = {"autosize": True}
        figure = self.visualiser.build(layout_elements=figure_layout_elements,width=66,height=66)
        return [figure]

    def _build_accordian(self,item):
        if isinstance(item,dict):
            summs = []
            for k,v in item.items():
                if len(v) == 0:
                    summs+= self.create_paragraph(k,className="detail_p")
                else:
                    children =  self.create_summary(k,k) + self.create_div("panel",self._build_accordian(v))
                    summs += self.create_detail(k,children)
            return summs
        elif isinstance(item,list):
            summary_list = []
            for element in item:
                summary_list += self._build_accordian(element)
            return summary_list
        else:
            return self.create_paragraph(item)


