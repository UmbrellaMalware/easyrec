import copy
import graphlib
import json

from app.f import data_2


class Edge:
    def __init__(self, name, dependencies, references=0):
        self.name = name
        self.dependencies = dependencies
        self.references = references

    def downgrade(self):
        self.references -= 1
        for dep in self.dependencies:
            dep.downgrade()

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name} -> {self.references}"

    def __eq__(self, other):
        return self.name == other.name


def in_edges(name, edges):
    for edge in edges:
        if edge.name == name:
            return True
    return False


def build_graph_from_requirements(requirements: dict):
    edges_map = {}
    for name in requirements.keys():
        name = name.split("==")[0]
        edges_map[name] = Edge(name, [], 0)
    for name, dependencies in requirements.items():
        name = name.split("==")[0]
        for dep in dependencies[1:]:
            dep_name = dep["name"].split("==")[0]
            if dep_name in edges_map:
                edge = edges_map[dep_name]
                edge.references += 1
                edge.is_dependency = True
                parent_edge = edges_map[name]
                parent_edge.dependencies.append(edge)
    return edges_map


def optimize(graph):
    sorted_edges = sorted(graph.values(), key=lambda x: x.references)
    optimized = copy.deepcopy(graph)
    for edge in sorted_edges:
        dependencies = edge.dependencies
        for dependency in dependencies:
            for dep in dependency.dependencies:
                name = dep.name
                dep.downgrade()
                if name == 'pyparsing':
                    print(dep)
                if name in optimized and dep.references <= 1:
                    to_downgrade = optimized.pop(name, [])
                    to_downgrade.downgrade()
    return list(optimized.keys())


data = {
    "django": ["six", "sql", "pytz", "sqlparce", "certifi"],
    "django_rest": ["six", "django"],
    "django_p": ["django", "django_b"],
    "django_b": ["django"],
    "celery": [],
    "flower": ["celery"],
    "six": [],
    "sql": [],
    "pytz": [],
    "sqlparce": ["six"],
    "aiohttp": ["certifi"],
    "twilio": ["certifi"],
    "certifi": [],
    "app": ["app2", "certifi", "app3"],
    "app3": ["certifi"],
    "app2": ["certifi", "app3"],
}
new_data = {}
for k, v in data.items():
    if k not in new_data:
        new_data[k] = [{"name": k}]
    for i in v:
        new_data[k].append({"name": i})
# print(data)
data = json.loads(open("data.json", "r").read())
g = build_graph_from_requirements(data)

# print(g)
optimized = optimize(g)
print(optimized)
print(len(data))
print(len(optimized))
