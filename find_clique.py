'''
Find first max-size clique in grapth
'''
import threading
import time
from contextlib import contextmanager

import networkx as nx
from networkx.algorithms.approximation import max_clique

import _thread

GLOBAL_MAX_CLIQUE = set()
'''
our maximum clique
'''


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException()
    finally:
        timer.cancel()


def time_it(func):
    '''
    Measures time
    '''
    def wrap(*args):
        time1 = time.time()
        ret = func(*args)
        time2 = time.time()
        print('\n{0} function took {1:.3f} ms'.format(
            func.__name__, (time2 - time1) * 1000.0))
        return ret
    return wrap


def read_args():
    '''
    Read our arguments
    '''
    import argparse
    parser = argparse.ArgumentParser(
        description="Find first maxsize clique for grapth specified in --path param.\
        May be limited in time with --time param")
    parser.add_argument('--path', type=str, default="/home/pavel/repos/max_clique_bnb/data/myciel3.col",
                        help='Path to graph dimacs-like format file')
    parser.add_argument('--time', type=int, default=120,
                        help='Time limit in seconds')
    return parser.parse_args()


def parse_graph(path):
    '''
    Parse .col file and return Networkx object
    '''
    edges_list = []
    with open(path, 'r') as g_file:
        for edge_line in g_file:
            # edge_line starts with p contains num_of_vertices and num_of_edges
            if edge_line.startswith('p'):
                _, name, vertices_num, edges_num = edge_line.split()
                print('{0} {1} {2}'.format(name, vertices_num, edges_num))
            elif edge_line.startswith('e'):
                _, v1, v2 = edge_line.split()
                edges_list.append((v1, v2))
            else:
                continue
        return nx.Graph(edges_list)


def find_max_clique_approx(graph_):
    '''
    Wrapper for suitable time estimation
    '''
    return max_clique(graph_)


def bnb_get_max_clique(graph_):
    global GLOBAL_MAX_CLIQUE
    guano = set()
    bb_recurcive(guano, graph_, graph_.nodes())
    return GLOBAL_MAX_CLIQUE


def bb_recurcive(curr_cliuqe, graph_, c_node_list):
    global GLOBAL_MAX_CLIQUE
    '''
    recursivly change global var GLOBAL_MAX_CLIQUE
    '''
    if(len(c_node_list) == 0):
        if len(curr_cliuqe) > len(GLOBAL_MAX_CLIQUE):
            GLOBAL_MAX_CLIQUE = curr_cliuqe
            curr_cliuqe = set(list(curr_cliuqe)[:len(curr_cliuqe) - 1])
    else:
        guanos = [node for node in sorted(
            nx.degree(graph_), key=lambda x: x[1], reverse=False)]
        c_node_list = set([it[0] for it in guanos])
        for c_node in c_node_list:
            if graph_.degree(c_node) + len(curr_cliuqe) < len(GLOBAL_MAX_CLIQUE):
                continue
            buff = curr_cliuqe.copy()
            new_c_list = c_node_list & set(graph_.neighbors(c_node))
            if(len(new_c_list) + len(curr_cliuqe) + 1 >= len(GLOBAL_MAX_CLIQUE)):
                buff.add(c_node)
                graph_buff = graph_.copy()
                graph_buff.remove_nodes_from(graph_.nodes() - new_c_list)
                bb_recurcive(buff, graph_buff, new_c_list)

@time_it
def find_max_clique_global(graph_):
    '''
    Branch and bound implementation, naive
    '''
    return bnb_get_max_clique(graph_)


def main():
    args = read_args()
    graph = parse_graph(args.path)
    try:
        with time_limit(args.time):
            GLOBAL_MAX_CLIQUE = find_max_clique_approx(graph)
            max_clq = find_max_clique_global(graph)
            print(max_clq, len(max_clq))
    except KeyboardInterrupt:
        print("Interrupted! current maximum clique: ", GLOBAL_MAX_CLIQUE, len(GLOBAL_MAX_CLIQUE))
    except TimeoutException:
        print("Timed out! current maximum clique: ", GLOBAL_MAX_CLIQUE, len(GLOBAL_MAX_CLIQUE))


if __name__ == '__main__':
    main()
