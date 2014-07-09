#!/usr/bin/env python
# -*- coding: utf-8 -*-
# file: {}
"""
A great python script.
"""
#from networkx.drawing.nx_pydot import write_dot

__author__ = 'rockyroad'

import time

from git import Repo

import pygraphviz as pgv # much lighter

def iso_date(seconds_since_epoch):
    return time.strftime("%F %T %Z", time.localtime(seconds_since_epoch))
    #time.strftime("%F %T GMT", time.gmtime(seconds_since_epoch))

def commit_info(commit):
    info = "Date: " + iso_date(commit.committed_date) + "\n"
    info += "Author: " + commit.author.name + " <" + commit.author.email + ">\n"
    info += "Parents: " + ' '.join([p.hexsha[:7] for p in commit.parents]) + "\n"
    info += "Message: "  + commit.message

    return info

def commit_names(commit):
    names = commit.name_rev.split(' ')
    assert names[0] == commit.hexsha
    return [name for name in names[1:] if not '~' in name]


class RepoView(object):
    """
    We can traverse history only by looking up parents.

    We can limit scope to a date range.

    We can limi
    """
    def __init__(self, path):
        """

        :param path:
        """
        self.repo = Repo(path)

    def graph(self, scope='HEAD~10..'):
        """
        >>> rv = RepoView("/tmp/s2m-flask2")
        >>> rv.graph('rr-fork..')

        :param scope:
        :return:
        """
        #G = nx.DiGraph()
        G = pgv.AGraph(strict=False, directed=True)
        G.node_attr.update(shape= 'box', color='blue', style="filled", fillcolor='#ddddff')
        name_attr = dict(shape='ellipse', color='red', fillcolor='#ffffaa')
        edges = {}
        for commit in self.repo.iter_commits(rev=scope):
            #the id must start with a letter
            id = 'C_' + commit.hexsha[:7]
            # the label or tooltip linebreaks must be escaped
            msg = commit.message.strip().replace("\n",'\l') + '\l' # left-justified line breaks
            print id, msg
            #
            G.add_node(id, label=msg, tooltip=commit.hexsha)
            for name in commit_names(commit):
                attr = name_attr
                # show remote branches label with different color
                if '/' in name:
                    name = name.split('/')[-1]
                    attr.update(fillcolor='#ffaa88')
                G.add_node(name, **attr)
                G.add_edge(name, id, arrowhead="none", color="red")
            # We need to have the nodes defined before edges, or attributes may be lost
            edges[id] = [ 'C_' + p.hexsha[:7] for p in commit.parents]

        # Now define the edges
        for id, grp in edges.iteritems():
            for edge in grp:
                G.add_edge(edge, id)
        return G

    def show_log(self, rev, **kwargs):
        """
        >>> rv = RepoView("/tmp/s2m-flask2")
        >>> rv.show_log('HEAD~2..')
        :param rev:
        :param kwargs:
        """
        for commit in self.repo.iter_commits(rev, **kwargs):
            print commit_info(commit)



def run(args):
    """
    Does great things.
    """
    #v = RepoView("/usr/local/www/s2m-flask")
    v = RepoView(args.repository)
    G = v.graph(scope=args.scope)
    G.write(args.name + '.dot')
    G.layout(prog=args.layout)
    G.draw(args.name + '.' + args.type)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", help="Path of your project's git repository")
    parser.add_argument("-s", "--scope", default="HEAD~10..",
                        help="The revision range to examine. Default: HEAD~10..")
    parser.add_argument("-n", "--name", default="/tmp/graph",
                        help="output file name, without extension. Default: /tmp/graph")
    parser.add_argument("-t", "--type", default="svg",
                        help="image file type (many choices, see graphviz documentation. Default: svg",
    )
    parser.add_argument("-l", "--layout", default="dot",
                        #choices=['dot', 'neato', 'circo', 'twppi', 'fdp', 'nop'],
                        help="graphviz layout program. default: dot",
                        )

    args = parser.parse_args()
    #print args.echo
    run(args)
