import dijkstar  # type: ignore
from typing import List
from typing_extensions import Self


class WaypointLayout:
    def __init__(self) -> None:
        self.graph = dijkstar.Graph()
        self.nodes: List[str] = []
        self.edges = 0

    def add_point(self, name: str) -> Self:
        self.nodes.append(name)
        return self

    def add_edge(self, u: str, v: str, weight: int = 1) -> Self:
        node_u = self.nodes.index(u)
        node_v = self.nodes.index(v)
        self.graph.add_edge(node_u, node_v, weight)
        self.graph.add_edge(node_v, node_u, weight)
        self.edges += 1
        return self

    def num_nodes(self) -> int:
        return len(self.nodes)

    def num_edges(self) -> int:
        return self.edges

    def shortest_path(self, s: str, t: str) -> List[str]:
        node_s = self.nodes.index(s)
        node_t = self.nodes.index(t)
        nodes = dijkstar.find_path(self.graph, node_s, node_t).nodes
        return [self.nodes[i] for i in nodes]


def smart_home_layout() -> WaypointLayout:
    layout = WaypointLayout()
    layout.add_point("P1").add_point("P2").add_point(
        "P3").add_point("P4").add_point("P5").add_point("P6")
    layout.add_point("living_room").add_point("kitchen").add_point(
        "bathroom").add_point("bedroom").add_point("guest_room").add_point("out")
    layout.add_edge("out", "P1").add_edge("P1", "P2").add_edge(
        "P2", "kitchen").add_edge("P2", "living_room")
    layout.add_edge("P2", "P3").add_edge("P3", "P4").add_edge(
        "P4", "bathroom").add_edge("P4", "P5")
    layout.add_edge("P5", "guest_room").add_edge(
        "P5", "P6").add_edge("P6", "bedroom")
    assert layout.num_nodes() == 12 and layout.num_edges() == 11
    return layout
