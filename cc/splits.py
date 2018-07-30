from itertools import combinations
from random import choices
from functools import reduce

class Split:
    def __init__(self, parent, child):
        assert len(parent) > len(child)
        assert len(child) > 0
        assert len(parent) > 2
        assert child.issubset(parent)
        self.parent = parent
        other_child = parent - child
        child_sorted = sorted(child)
        other_sorted = sorted(other_child)
        if child_sorted[0] < other_sorted[0]:
            self._child1 = frozenset(child)
            self._child1_sorted = child_sorted
            self._child2 = frozenset(other_child)
            self._child2_sorted = other_sorted
        else:
            self._child1 = frozenset(other_child)
            self._child1_sorted = other_sorted
            self._child2 = frozenset(child)
            self._child2_sorted = child_sorted
            
    def get_children(self):
        return self._child1, self._child2
    
    def get_parent(self):
        return frozenset.union(self._child1, self._child2)
    
    def __str__(self):
        return str(self._child1_sorted) + ' | ' + str(self._child2_sorted)
    
    def __eq__(self, other):
        return self.get_children() == other.get_children()
    
    def __repr__(self):
        return 'Split({0}, {1})'.format(set(self.get_parent()), set(self.get_children()[0]))
    
    def __hash__(self):
        return hash(self.get_children())

def get_clade(x):
    if isinstance(x, str):
        return frozenset({ x })
    elif isinstance(x, TreeNode):
        return x.get_clade()
    else:
        raise ValueError('Invalid input to get_clade: {0}'.format(repr(x)))

def node_to_string(x, child_format):
    if isinstance(x, str):
        return x
    elif isinstance(x, TreeNode):
        child1, child2 = x.get_children()
        return child_format.format(str(child1), str(child2))
    else:
        assert False

class TreeNode:
    def __init__(self, child1, child2):
        child1_clade = get_clade(child1)
        child2_clade = get_clade(child2)

        assert len(frozenset.intersection(child1_clade, child2_clade)) == 0
        self._clade = frozenset.union(child1_clade, child2_clade)

        child1_first = min(child1_clade)
        child2_first = min(child2_clade)

        if child1_first < child2_first:
            self._child1 = child1
            self._child2 = child2
        else:
            self._child2 = child1
            self._child1 = child2
        
        
    def get_clade(self):
        return self._clade
            
    def get_children(self):
        return self._child1, self._child2
    
    def __str__(self):
        return node_to_string(self, '({0},{1})')
    
    def __eq__(self, other):
        return self.get_children() == other.get_children()

    def __repr__(self):
        return node_to_string(self, 'TreeNode({0},{1})')
    
    def __hash__(self):
        return hash(self.get_children())
    
def get_splits(clade):
    n = len(clade)
    clade_sorted = sorted(clade)
    first_slice = clade_sorted[:1]
    others = clade_sorted[1:]
    for k in range(n-1):
        for combination in combinations(others, k):
            yield Split(clade, set(list(combination) + first_slice))

def prod(xs):
    res = 1.0
    for x in xs:
        res *= x
    return res

def get_split_p(clade, split, split_ps):
    if clade in split_ps:
        if split in split_ps[clade]:
            return split_ps[clade][split]
        else:
            return 0.0
    else:
        return 0.0

def tree_split_p(tree, split_ps):
    if isinstance(tree, str):
            return 1.0
    else:
        children = tree.get_children()
        if all([isinstance(child, str) for child in children]):
            return 1.0
        else:
            clade = tree.get_clade()
            subtree_p_approxs = [tree_split_p(subtree, split_ps) for subtree in children]
            split = Split(clade, get_clade(children[0]))
            split_p = get_split_p(clade, split, split_ps)
            return split_p*prod(subtree_p_approxs)

def sample_tree(clade, split_ps):
    if len(clade) == 1:
        return list(clade)[0] 
    elif len(clade) == 2:
        return TreeNode(*clade)
    elif len(clade) > 2:
        clade_split_ps = split_ps[clade]
        splits = list(clade_split_ps.keys())
        ps = list(clade_split_ps.values())
        split = choices(splits, ps)[0]
        return TreeNode(*[sample_tree(child_clade, split_ps) for child_clade in split.get_children()])
    else: 
        raise ValueError('Clade must not be empty')


def split_dict_reduce(clades, clade_splits, function, dict_sequence, initial_dict=None):
    res = {}
    for clade in clades:
        res[clade] = {}
        for split in clade_splits[clade]:
            clade_split_vals = [dict_[clade][split] for dict_ in dict_sequence]
            initial = None if initial_dict is None else initial_dict[clade][split]
            res[clade][split] = reduce(function, clade_split_vals, initial)
    return res


def split_dict_zip_apply(clades, clade_splits, function, dict_sequence):
    res = {}
    for clade in clades:
        res[clade] = {}
        for split in clade_splits[clade]:
            clade_split_vals = [dict_[clade][split] for dict_ in dict_sequence]
            res[clade][split] = function(clade_split_vals)
    return res

def split_dict_apply(clades, clade_splits, function, split_dict):
    res = {}
    for clade in clades:
        res[clade] = {}
        for split in clade_splits[clade]:
            res[clade][split] = function(split_dict[clade][split])
    return res
