#!/usr/bin/env python
# -*- coding: utf-8 -*-
# file: {}
"""
A great python script.
"""
#from networkx.drawing.nx_pydot import write_dot

__author__ = 'rockyroad'

from git import Repo
import time
#import networkx as nx #I don't need this complexity
import pygraphviz as pgv # much lighter

def tuto():
    """
    >>> repo = Repo("/tmp/s2m-flask2")
    >>> assert repo.bare == False
    >>> repo.heads
    [<git.Head "refs/heads/s2m">, <git.Head "refs/heads/sa_blog">]
    >>> repo.heads.s2m
    <git.Head "refs/heads/s2m">
    >>> repo.heads.master
    Traceback (most recent call last):
    AttributeError: 'IterableList' object has no attribute 'master'
    >>> repo.tags
    [<git.TagReference "refs/tags/rr-fork">]
    >>> repo.tags[0].tag
    >>> repo.tags[0].commit
    <git.Commit "25b8d1ac2376daed2e3cef8253ef1f48bbd4718d">
    >>> head = repo.head            # the head points to the active branch/ref
    >>> head
    <git.HEAD "HEAD">
    >>> master = head.reference     # retrieve the reference the head points to
    >>> master.commit               # from here you use it as any other reference
    <git.Commit "bed053145a6f18a3ead215ab579ccd6d0b0f1a82">
    >>> repo.commit('HEAD~10')
    <git.Commit "f3a13eff24287587c846a5520498820cbb5d6b5f">
    >>> origin = repo.remotes.origin
    >>> origin.refs
    [<git.RemoteReference "refs/remotes/origin/HEAD">, <git.RemoteReference "refs/remotes/origin/apidoc">, <git.RemoteReference "refs/remotes/origin/contacts">, <git.RemoteReference "refs/remotes/origin/flaskr">, <git.RemoteReference "refs/remotes/origin/gh-pages">, <git.RemoteReference "refs/remotes/origin/master">, <git.RemoteReference "refs/remotes/origin/req-upgrade">, <git.RemoteReference "refs/remotes/origin/sa_blog">]

    """
    pass


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
                G.add_edge(name, id)
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



def run():
    """
    Does great things.
    """
    #v = RepoView("/tmp/s2m-flask2")
    v = RepoView("/usr/local/www/s2m-flask")
    G = v.graph(scope='rr-fork..')
    #nx.draw_graphviz(G)
    #write_dot(G, 'graph.dot')
    #A = nx.to_agraph(G)
    #A.write('Agraph.dot')
    #nx.draw_networkx(G) #,'graph.png')
    G.write('graph.dot')
    G.layout(prog='dot')
    #G.layout(prog='neato')
    G.draw('graph.svg')
    #G.draw('graph.ps', prog='circo'

if __name__ == '__main__':
    run()
