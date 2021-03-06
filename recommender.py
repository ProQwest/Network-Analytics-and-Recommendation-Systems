import igraph
import random,sys
import json, csv

def load_description(filename):
    reader = csv.reader(open(filename, 'rb'))
    description_map = dict(x for x in reader)
    return description_map

global description_map 
description_map = load_description('/Users/umang/Desktop/MTP/Code/descriptions/description_map.csv')

def load_graph(language):
    language_file = "/Users/umang/Desktop/MTP/Code/Communities/" + language + ".gml"
    g = igraph.read(language_file)
    return g

def test():
    community_graph = load_graph("Communities/C++.gml")
    for node in community_graph.vs:
        if len(node.neighbors()) > 0 : print node['name'], node['watchers'], node['label']

def search_node(query_repository, language_graph):
    for node in language_graph.vs:
        if node['label'] == query_repository:
            return node
    return None

# Function for filtering out the top watched repositories which do not have any edges. This is for adding granularity to the recommendations

def indepedent_suggestions(language_graph, number):
    global description_map
    repo_watcher_map = {}
    for node in language_graph.vs : 
        if len(node.neighbors()) == 0 :
            repo_watcher_map[node['name']] = node['watchers']
    top_repos = sorted(repo_watcher_map.items(), key=lambda e: e[1], reverse=True)[0:20]
    random.shuffle(top_repos)
    suggestions = []
    for key,value in top_repos:
        description = description_map[key[19:]]
        suggestions.append([key,description])
    return suggestions[0:number]

#Function for returning recommendations on the basis of pagerank of all nodes

def far_off_suggestions(language_graph, number): 
    page_ranks = language_graph.pagerank()
    pagerank_map = {}
    for index in range(len(page_ranks)):
        pagerank_map[index] = page_ranks[index]
    top_repos = sorted(pagerank_map.items(),key=lambda e: e[1], reverse=True)[0:25]
    random.shuffle(top_repos)
    suggestions = []
    for id in top_repos:
        name = language_graph.vs[id]['name'][0]
        description = description_map[name[19:]]
        suggestions.append([name,description])
    return suggestions[0:number]


def make_json(suggestions):
    suggestions_map = {}
    for rank in range(1,len(suggestions)):
        suggestions_map[rank] = suggestions[rank-1]
    suggestions_json = json.dumps(suggestions_map)
    return suggestions_json

# Main recommender function that calls all the other auxillarily recommendor functions
    # Suggestions comprise of upto 10 nodes in the order 2 immediate neighborhood, upto 5 
    # far off suggestions and upto 5 independent node suggestions
def recommender(query_repository , language):
    
    #Loading the given language file
    language_graph = load_graph(language)

    #Searching the given repository in the logs
    root_node = search_node(query_repository, language_graph)
    
    if root_node is None :
        print "Sorry the given repository cannot be found in the logs"
        sys.exit()

    #Looking in the order = 2 neighboorhood
    neighborhood_node_ids = language_graph.neighborhood(int(root_node['id']),order=2)

    #Fetching suggested repository names and appendings suggestions rank wise
    suggestions = []
    for id in neighborhood_node_ids : 
        name = language_graph.vs[id]['name']
        description = description_map[name[19:]]
        suggestions.append([name,description])
    suggestions = suggestions[0:10] + far_off_suggestions(language_graph, 5) + indepedent_suggestions(language_graph, 5)

    return json.dumps(suggestions)


def main():
    # python recommender.py -r pydata/pandas -l Python
    first_arg = sys.argv[1]
    if first_arg == '-t':
        language_graph = load_graph(sys.argv[2].capitalize())
        print json.dumps(far_off_suggestions(language_graph,10))
    elif first_arg == '-r':
        input_repository = sys.argv[2]
        input_language = sys.argv[4]
        print recommender(sys.argv[2], sys.argv[4].capitalize())
    else:
        return [None]

main()


### Sample example commands for demonstration
"""
    python recommender.py -r pydata/pandas -l python
    python recommender.py -r facebook/folly -l c++
    python recommender.py -r facebook/hhvm -l C++ 

    python recommender.py -t python
"""
