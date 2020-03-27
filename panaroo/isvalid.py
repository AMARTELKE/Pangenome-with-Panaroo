import os, sys
try:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
except ImportError:
    from io import StringIO
from ast import literal_eval
from collections import defaultdict
import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import open_file
from intbitset import intbitset

import re
try:
    import htmlentitydefs
except ImportError:
    # Python 3.x
    import html.entities as htmlentitydefs

try:
    long
except NameError:
    long = int
try:
    unicode
except NameError:
    unicode = str
try:
    unichr
except NameError:
    unichr = chr
try:
    literal_eval(r"u'\u4444'")
except SyntaxError:
    # Remove 'u' prefixes in unicode literals in Python 3
    def rtp_fix_unicode(s):
        return s[1:]
else:
    rtp_fix_unicode = None


def escape(text):
    """Use XML character references to escape characters.

    Use XML character references for unprintable or non-ASCII
    characters, double quotes and ampersands in a string
    """
    def fixup(m):
        ch = m.group(0)
        return '&#' + str(ord(ch)) + ';'

    text = re.sub('[^ -~]|[&"]', fixup, text)
    return text if isinstance(text, str) else str(text)


def unescape(text):
    """Replace XML character references with the referenced characters"""
    def fixup(m):
        text = m.group(0)
        if text[1] == '#':
            # Character reference
            if text[2] == 'x':
                code = int(text[3:-1], 16)
            else:
                code = int(text[2:-1])
        else:
            # Named entity
            try:
                code = htmlentitydefs.name2codepoint[text[1:-1]]
            except KeyError:
                return text  # leave unchanged
        try:
            return chr(code) if code < 256 else unichr(code)
        except (ValueError, OverflowError):
            return text  # leave unchanged

    return re.sub("&(?:[0-9A-Za-z]+|#(?:[0-9]+|x[0-9A-Fa-f]+));", fixup, text)


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


def is_valid_folder(parser, arg):
    if not os.path.isdir(arg):
        parser.error("The folder %s does not exist!" % arg)
    else:
        return arg


def conv_list(maybe_list):
    if not isinstance(maybe_list, list):
        maybe_list = [maybe_list]
    return (maybe_list)


def del_dups(seq):
    seen = set()
    pos = 0
    for item in seq:
        if item not in seen:
            seen.add(item)
            seq[pos] = item
            pos += 1
    del seq[pos:]
    return (seq)


def custom_stringizer(value):
    """Convert a `value` to a Python literal in GML representation.

    Parameters
    ----------
    value : object
        The `value` to be converted to GML representation.

    Returns
    -------
    rep : string
        A double-quoted Python literal representing value. Unprintable
        characters are replaced by XML character references.

    Raises
    ------
    ValueError
        If `value` cannot be converted to GML.

    Notes
    -----
    `literal_stringizer` is largely the same as `repr` in terms of
    functionality but attempts prefix `unicode` and `bytes` literals with
    `u` and `b` to provide better interoperability of data generated by
    Python 2 and Python 3.

    The original value can be recovered using the
    :func:`networkx.readwrite.gml.literal_destringizer` function.
    """
    def stringize(value):
        if isinstance(value, (int, long, bool)) or value is None:
            if value is True:  # GML uses 1/0 for boolean values.
                buf.write(str(1))
            elif value is False:
                buf.write(str(0))
            else:
                buf.write(str(value))
        elif isinstance(value, unicode):
            text = repr(value)
            if text[0] != 'u':
                try:
                    value.encode('latin1')
                except UnicodeEncodeError:
                    text = 'u' + text
            buf.write(text)
        elif isinstance(value, (float, complex, str, bytes)):
            buf.write(repr(value))
        elif isinstance(value, list):
            buf.write('[')
            first = True
            for item in value:
                if not first:
                    buf.write(',')
                else:
                    first = False
                stringize(item)
            buf.write(']')
        elif isinstance(value, set):
            buf.write('[')
            first = True
            for item in value:
                if not first:
                    buf.write(',')
                else:
                    first = False
                stringize(item)
            buf.write(']')
        elif isinstance(value, intbitset):
            buf.write('[')
            first = True
            for item in value:
                if not first:
                    buf.write(',')
                else:
                    first = False
                stringize(item)
            buf.write(']')
        elif isinstance(value, tuple):
            if len(value) > 1:
                buf.write('(')
                first = True
                for item in value:
                    if not first:
                        buf.write(',')
                    else:
                        first = False
                    stringize(item)
                buf.write(')')
            elif value:
                buf.write('(')
                stringize(value[0])
                buf.write(',)')
            else:
                buf.write('()')
        elif isinstance(value, dict):
            buf.write('{')
            first = True
            for key, value in value.items():
                if not first:
                    buf.write(',')
                else:
                    first = False
                stringize(key)
                buf.write(':')
                stringize(value)
            buf.write('}')
        elif isinstance(value, set):
            buf.write('{')
            first = True
            for item in value:
                if not first:
                    buf.write(',')
                else:
                    first = False
                stringize(item)
            buf.write('}')
        else:
            raise ValueError('%r cannot be converted into a Python literal' %
                             (value, ))

    buf = StringIO()
    stringize(value)
    return buf.getvalue()


# Author: Nicholas Mancuso (nick.mancuso@gmail.com)
from networkx.utils import arbitrary_element


def ramsey_R2(G):
    """Approximately computes the Ramsey number `R(2;s,t)` for graph.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    max_pair : (set, set) tuple
        Maximum clique, Maximum independent set.
    """
    if not G:
        return set(), set()

    node = arbitrary_element(G)
    nbrs = set(nx.all_neighbors(G, node))
    nbrs.discard(node)
    nnbrs = nx.non_neighbors(G, node)
    c_1, i_1 = ramsey_R2(G.subgraph(nbrs).copy())
    c_2, i_2 = ramsey_R2(G.subgraph(nnbrs).copy())

    c_1.add(node)
    i_2.add(node)
    # Choose the larger of the two cliques and the larger of the two
    # independent sets, according to cardinality.
    return max(c_1, c_2, key=len), max(i_1, i_2, key=len)


def max_clique(G):
    """Find the Maximum Clique

    Finds the `O(|V|/(log|V|)^2)` apx of maximum clique/independent set
    in the worst case.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    clique : set
        The apx-maximum clique of the graph

    Notes
    ------
    A clique in an undirected graph G = (V, E) is a subset of the vertex set
    `C \subseteq V`, such that for every two vertices in C, there exists an edge
    connecting the two. This is equivalent to saying that the subgraph
    induced by C is complete (in some cases, the term clique may also refer
    to the subgraph).

    A maximum clique is a clique of the largest possible size in a given graph.
    The clique number `\omega(G)` of a graph G is the number of
    vertices in a maximum clique in G. The intersection number of
    G is the smallest number of cliques that together cover all edges of G.

    http://en.wikipedia.org/wiki/Maximum_clique

    References
    ----------
    .. [1] Boppana, R., & Halldórsson, M. M. (1992).
        Approximating maximum independent sets by excluding subgraphs.
        BIT Numerical Mathematics, 32(2), 180–196. Springer.
        doi:10.1007/BF01994876
    """
    sys.setrecursionlimit(int(10e6))

    if G is None:
        raise ValueError("Expected NetworkX graph!")

    # finding the maximum clique in a graph is equivalent to finding
    # the independent set in the complementary graph
    cgraph = nx.complement(G)
    iset, _ = clique_removal(cgraph)
    return iset


def clique_removal(G):
    """ Repeatedly remove cliques from the graph.

    Results in a `O(|V|/(\log |V|)^2)` approximation of maximum clique
    & independent set. Returns the largest independent set found, along
    with found maximal cliques.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    max_ind_cliques : (set, list) tuple
        Maximal independent set and list of maximal cliques (sets) in the graph.

    References
    ----------
    .. [1] Boppana, R., & Halldórsson, M. M. (1992).
        Approximating maximum independent sets by excluding subgraphs.
        BIT Numerical Mathematics, 32(2), 180–196. Springer.
    """
    graph = G.copy()
    c_i, i_i = ramsey_R2(graph)
    cliques = [c_i]
    isets = [i_i]
    while graph:
        graph.remove_nodes_from(c_i)
        c_i, i_i = ramsey_R2(graph)
        if c_i:
            cliques.append(c_i)
        if i_i:
            isets.append(i_i)

    maxiset = max(isets)
    return maxiset, cliques