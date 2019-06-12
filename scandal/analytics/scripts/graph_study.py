import graph
import csv 
from glob import glob
import sys
import os
import numpy as np
import pandas as pd
import re
from py2neo import Graph, Node, Relationship, NodeMatcher
from datetime import datetime
from dateutil.relativedelta import relativedelta
# from py2neo.data import Node, Relationship
from tqdm import tqdm

uri = "bolt://localhost:7687"
user = "neo4j"
password = "spring2019"
#https://py2neo.org/v3/database.html
graph = Graph(uri=uri, user=user, password=password)
matcher = NodeMatcher(graph)

def get_longest_path() :
    # dict_relations = graph.run('MATCH (n:User)-[r:RETWEETED]-(m:User) \
    #         RETURN n.author,r,m.author LIMIT ' + str(500)).data()
    #https://stackoverflow.com/questions/41805735/cypher-query-to-find-the-longest-path-using-neo4j-3-1-0-version
    #https://stackoverflow.com/questions/41789561/find-longest-path-in-graph
    dict_relations = graph.run('match (n)\
        where (n)-[:REPLIED_TO]->() and not ()-[:REPLIED_TO]->(n)\
        match p = (n)-[:REPLIED_TO*1..]->(m)\
        return p, length(p) as L\
        order by L desc LIMIT 1').data()
    return dict_relations

def print_longest_path() :
    dict_relations = graph.run('match (n)\
        where (n)-[:RETWEETED]->() and not ()-[:RETWEETED]->(n)\
        match p = (n)-[:RETWEETED*1..]->(m)\
        return p, length(p) as L').data()
        # order by L desc LIMIT 5
    # dict_relations = graph.run('match (n)\
    #     match p = (n)-[:RETWEETED*..]->(m)\
    #     return p, length(p) as L\
    #     order by L desc LIMIT 5').data()
    total_ = []
    for item in dict_relations:
        total_.append(item['L'])
    average = sum(total_)*1./len(total_)*1.
    return sum(total_), len(total_), average

#https://stackoverflow.com/questions/42238183/neo4j-query-to-find-the-nodes-with-most-relationships-and-their-connected-node
def get_breadth():
    # dict_relations = graph.run('MATCH (n:User)-[:REPLIED_TO]->(m)\
    #     WITH m, SIZE((n)-[:REPLIED_TO]->()) as mostNodesCnt\
    #     where (n)-[:REPLIED_TO]->() and not ()-[:REPLIED_TO]->(n)\
    #     RETURN mostNodesCnt\
    #     ORDER BY mostNodesCnt DESC LIMIT 1').data()
    # dict_relations = graph.run('MATCH p = (n:User)-[:REPLIED_TO]->()\
    #     WITH n, COLLECT(p) AS paths\
    #     where (n)-[:REPLIED_TO]->() and not ()-[:REPLIED_TO]->(n)\
    #     RETURN n, REDUCE(s = paths[0], x IN paths[1..] | CASE WHEN LENGTH(x) < LENGTH(s) THEN x ELSE s END) AS path\
    #     limit 10').data()
    dict_relations = graph.run('match (n)\
        WITH SIZE((n)-[:RETWEETED]->()) as mostNodesCnt\
        where (n)-[:RETWEETED]->() and not ()-[:RETWEETED]->(n)\
        match p = (n)-[:RETWEETED*1..]->(m)\
        return mostNodesCnt, length(p) as L ORDER BY mostNodesCnt desc LIMIT 3').data()
    return dict_relations

def get_size():
    dict_relations = graph.run('MATCH (n:User)-[r:RETWEETED]-(m:User) \
            where (n)-[:RETWEETED]->() and not ()-[:RETWEETED]->(n)\
            RETURN DISTINCT n.author,r,m.author').data()
    # dict_relations = graph.run('MATCH (n:User)\
    #     WITH n, COUNT(DISTINCT(()-[:REPLIED_TO]->(n))) as NodesCnt\
    #     RETURN NodesCnt').data()
    size = len(dict_relations)
    return size

# def get_size():
#     dict_relations = graph.run('MATCH (n:User)-[r:MENTIONED]-(m:User), \
#             p = shortestPath((n)-[*..15]-(m))\
#             RETURN length(p)').data()
#     # dict_relations = graph.run('MATCH (n:User)\
#     #     WITH n, COUNT(DISTINCT(()-[:REPLIED_TO]->(n))) as NodesCnt\
#     #     RETURN NodesCnt').data()
#     size = len(dict_relations)
#     return size

def get_totals() :
    dict_relations = graph.run('match (n) return length(n) as T').data()
    return dict_relations


print(get_breadth())