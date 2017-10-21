'''
Find first maxsize clique for grapth
'''
import threading
import time
from contextlib import contextmanager

import networkx as nx
from networkx.algorithms.approximation import max_clique

import _thread

class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    timer = threading.Timer(seconds, lambda:_thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException()
    finally:
        timer.cancel()


def time_it(f):
    '''
    Measures time
    '''
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('\n{0} function took {1:.3f} ms'.format(
            f.__name__, (time2 - time1) * 1000.0))
        return ret
    return wrap


def read_args():
    '''
    Let's read our argumens
    '''
    import argparse
    parser = argparse.ArgumentParser(
        description="Find first maxsize clique for grapth specified in --path param.\
        May be limited in time with --time param")
    parser.add_argument('--path', type=str, required=True,
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


@time_it
def find_max_clique(G):
    return max_clique(G)


def main():
    args = read_args()
    graph = parse_graph(args.path)
    try:
        with time_limit(args.time):
            max_clq = find_max_clique(graph)
            print(max_clq, len(max_clq))
    except TimeoutException:
        print("Timed out!")


if __name__ == '__main__':
    main()
