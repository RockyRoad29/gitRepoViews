#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Michelle Baert

"""
Builds graphics representation of a project's GIT history

"""

__author__ = 'rockyroad'

import time, logging
import git
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

#         G = pgv.AGraph(strict=False, directed=True)

class RepoGraph():
    """
    In this version I am going to try to keep commit hash as node ids,
    while showing commit messages separately.

    @todo alternative graph separating each branch in its own cluster
    http://graphviz.org/Gallery/directed/cluster.html
    """

    def __init__(self, repo_path, **attr):
        self.G = pgv.AGraph(name="gitGraph", strict=False, directed=True, **attr)
        self.repo = git.Repo(repo_path)
        self.G.node_attr.update(shape= 'box', color='blue', style="filled", fillcolor='#ddddff')
        self.name_attr = dict(shape='ellipse', color='red', fillcolor='#ffffaa')
        self.git_flow = {}


    def add_commit(self, commit, show_message=True):
        #the id must start with a letter
        short_id = commit.hexsha[:7]
        node_id = 'C_' + short_id
        if self.G.has_node(node_id):
            logging.info("%s is already a node, skipping", node_id)
            return node_id
            # the label or tooltip linebreaks must be escaped

        bunch = [node_id]
        self.G.add_node(node_id, label=short_id)

        # Show the commit message
        if show_message:
            msg = commit.message.strip().replace("\n", '\l') + '\l' # left-justified line breaks
            msg_id = 'M_' + short_id
            self.G.add_node(msg_id, shape="none", style="", label=msg, fontsize=10)
            self.G.add_edge(msg_id, node_id, weight=1, style="dotted", arrowhead="none")
            bunch.append(msg_id)

        # Show tags or heads
        for name in commit_names(commit):
            self.add_commit_name(node_id, name)
            bunch.append(name)

        # cluster_id = 'S_' + short_id
        # self.G.add_subgraph(nbunch=bunch, rank='same', name=cluster_id)
        # return cluster_id
        return node_id

    def add_commit_name(self, node_id, name):
        attr = self.name_attr
        # show remote branches label with different color
        if '/' in name:
            name = name.split('/')[-1]
            attr.update(fillcolor='#ffaa88')
        self.G.add_node(name, **attr)
        self.G.add_edge(name, node_id, arrowhead="none", color="red")

    def graph(self, scope=None):
        """
        >>> rv = RepoGraph(".")
        >>> rv.graph()

        :param scope:
        :return:
        """
        for commit in self.repo.iter_commits(rev=scope):
            node_id = self.add_commit(commit)
            self.git_flow[node_id] = []
            # We need to have the nodes defined before edges, or attributes may be lost
            for p in commit.parents:
                p_id = self.add_commit(p)
                self.git_flow[node_id].append(p_id)

        # Now define the edges
        for node_id, grp in self.git_flow.iteritems():
            assert node_id
            for edge in grp:
                assert edge
                logging.info("%s -> %s", edge, node_id)
                self.G.add_edge(edge, node_id, weight=3)
        return self.G

    def show_log(self, rev, **kwargs):
        """
        >>> rv = RepoGraph("/tmp/s2m-flask2")
        >>> rv.show_log('HEAD~2..')
        :param rev:
        :param kwargs:
        """
        for commit in self.repo.iter_commits(rev, **kwargs):
            print commit_info(commit)



def run(args):
    """
    Build the repository graph, and saves it as .dot and image

    @todo convert this to RepoGraph method, exposing arguments
    """
    #v = RepoGraph("/usr/local/www/s2m-flask")
    v = RepoGraph(args.repository)
    G = v.graph(scope=args.scope)
    # keep the dot source simple by saving it without pos info
    G.write(args.name + '.dot')

    # We can choose here our layout before generating image
    G.layout(prog=args.layout)
    G.draw(args.name + '.' + args.type)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", help="Path of your project's git repository")
    parser.add_argument("-s", "--scope",
                        #, default="HEAD~10.."
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
    print "Examining scope %s from repository %s" % (args.scope, args.repository)
    logging.basicConfig(level=logging.DEBUG)#, filename='gitGraph.log', filemode='w')
    run(args)
    print "Wrote %s.dot and %s.%s" %( args.name, args.name, args.type)
