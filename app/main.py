import copy
import json
from multiprocessing.pool import ThreadPool

from johnnydep import JohnnyDist
from johnnydep.logs import configure_logging


def get_deps(package_name):
    configure_logging(verbosity=0)
    try:
        dist = JohnnyDist(
            package_name,
        )
        rendered = dist.serialise(
            fields=["name"],
            format="json",
            recurse=True,
        )
        return package_name, json.loads(rendered)
    except Exception as e:
        print(e)
        return package_name, []


def find_in_rec(recs, name):
    for num, rec in enumerate(recs):
        rec_name = rec.split("==")[0]
        if rec_name == name:
            return num


def add_deps_to_graph(graph, deps, edge, recs):
    for dep in deps[1:]:
        indx = find_in_rec(recs, dep["name"])
        if indx is None:
            continue
        name = dep["name"]
        if edge not in graph:
            graph[edge] = []
        graph[edge].append(name)
    return graph


def get_all_deps(recs):
    all_deps = {}
    counter = 0
    with ThreadPool(10) as pool:
        for result in pool.map(get_deps, recs):
            counter += 1
            name, deps = result
            all_deps[name] = deps
    return all_deps


def start():
    recs = open("../requirements.txt", "r").readlines()
    recs = [rec.replace("\n", "") for rec in recs]
    new_rec = copy.deepcopy(recs)
    counter = 0
    count = len(recs)
    graph = {}
    rec_deps = get_all_deps(recs)
    print(rec_deps)
        # print(deps)
        # for dep in deps[1:]:
        #     name = dep["name"]
        #     if (find := find_in_rec(new_rec, name)) is not None:
        #         new_rec.pop(find)
    print(len(new_rec), len(recs))
    print(graph)
    o = open("../new_requirements.txt", "w")
    for rec in new_rec:
        o.write(rec + "\n")
    o.close()



start()