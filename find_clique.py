'''
Find first max-size clique in grapth
'''
import threading
import time
from contextlib import contextmanager

import networkx as nx
from networkx.algorithms.approximation import max_clique

import _thread

GLOBAL_MAX_CLIQUE = list()
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
    parser.add_argument('--path', type=str, default="/data/johnson8-2-4.clq.txt",
                        help='Path to graph dimacs-like format file')
    parser.add_argument('--time', type=int, default=300,
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
            if edge_line.startswith('e'):
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
    bb_recurcive(list(), graph_, list(graph_.nodes()))
    return GLOBAL_MAX_CLIQUE


def bb_recurcive(curr_clique, graph_, candidates_node_list):
    global GLOBAL_MAX_CLIQUE
    '''
    recursivly change global var GLOBAL_MAX_CLIQUE
    '''
    len_cur_c = len(curr_clique)  # size of current clique we want to expand
    len_global_c = len(GLOBAL_MAX_CLIQUE)  # size of current max clique
    # size of set with candidates able to expand our clique
    len_cand_list = len(candidates_node_list)
    if len_cand_list == 0:
        # if candidates list is empty, check that current clique may by our maximum
        if len_cur_c > len_global_c:
            GLOBAL_MAX_CLIQUE = curr_clique
            # throw last candidate out and give next candidates a chance
        curr_clique = curr_clique[:len_cur_c - 1]
    else:
        for c_node in candidates_node_list:
            # check for each candidate ability to overcome our current max clique
            if (graph_.degree(c_node) + len_cur_c) < len_global_c:
                continue
            buff = curr_clique.copy()
            new_cand_set = list(graph_.neighbors(c_node))
            if (len(new_cand_set) + len_cur_c + 1) >= len_global_c:
                buff.append(c_node)
                graph_buff = graph_.copy()
                graph_buff.remove_nodes_from(graph_.nodes() - new_cand_set)
                bb_recurcive(buff, graph_buff, new_cand_set)


@time_it
def find_max_clique(graph_):
    '''
    Branch and bound implementation, naive
    '''
    return bnb_get_max_clique(graph_)


def main():
    args = read_args()
    graph = parse_graph(args.path)
    try:
        with time_limit(args.time):
            max_clq = find_max_clique(graph)
            print(len(max_clq))
            print(max_clq)
    except KeyboardInterrupt:
        print("\n Interrupted! current maximum clique: ",
              GLOBAL_MAX_CLIQUE, len(GLOBAL_MAX_CLIQUE))
    except TimeoutException:
        print("\n Timed out! current maximum clique: ",
              GLOBAL_MAX_CLIQUE, len(GLOBAL_MAX_CLIQUE))


if __name__ == '__main__':
    main()
