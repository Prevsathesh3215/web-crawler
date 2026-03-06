import networkx as nx
import unicodedata
import re
from pyvis.network import Network
from IPython.display import IFrame

#KNOWLEDGE GRAPH CLASS
class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()


    @staticmethod
    def normalize_node(text):
      text = text.replace("_", " ")
      text = text.lower()
      text = unicodedata.normalize("NFKC", text)
      text = re.sub(r"\s+", " ", text)
      return text.strip()

    def build_graph(self, pages):
        for page in pages:
            title = self.normalize_node(page["title"])

            self.graph.add_node(title)

            for link in page["links"]:
                target = self.normalize_node(link.split("/wiki/")[-1])

                self.graph.add_edge(title, target)




#PYVIS
def visualize_graph(graph):
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=True,
        cdn_resources="in_line"
    )

    for node, data in graph.nodes(data=True):
        net.add_node(
            node,
            label=node,
            title=data.get("summary", ""),
            size=20
        )

    for source, target in graph.edges():
        net.add_edge(source, target)

        html = net.generate_html()

        with open("knowledge_graph.html", "w", encoding="utf-8") as f:
            f.write(html)
        IFrame("knowledge_graph.html", width=900, height=600)
