from itertools import combinations

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
    
def get_splits(clade):
    n = len(clade)
    clade_sorted = sorted(clade)
    first_slice = clade_sorted[:1]
    others = clade_sorted[1:]
    for k in range(n-1):
        for combination in combinations(others, k):
            yield Split(clade, set(list(combination) + first_slice))