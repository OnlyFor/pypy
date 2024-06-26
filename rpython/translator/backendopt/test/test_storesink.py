
import py
from rpython.rlib.nonconst import NonConstant
from rpython.translator.translator import TranslationContext, graphof
from rpython.translator.backendopt.storesink import storesink_graph
from rpython.translator.backendopt import removenoops
from rpython.flowspace.model import checkgraph
from rpython.conftest import option

class TestStoreSink(object):
    def translate(self, func, argtypes):
        t = TranslationContext()
        t.buildannotator().build_types(func, argtypes)
        t.buildrtyper().specialize()
        return t

    def check(self, f, argtypes, no_getfields=0):
        t = self.translate(f, argtypes)
        getfields = 0
        graph = graphof(t, f)
        removenoops.remove_same_as(graph)
        checkgraph(graph)
        storesink_graph(graph)
        checkgraph(graph)
        if option.view:
            t.view()
        for block in graph.iterblocks():
            for op in block.operations:
                if op.opname == 'getfield':
                    getfields += 1
        if no_getfields != getfields:
            py.test.fail("Expected %d, got %d getfields" %
                         (no_getfields, getfields))

    def test_infrastructure(self):
        class A(object):
            pass

        def f(i):
            a = A()
            a.x = i
            return a.x

        self.check(f, [int], 0)

    def test_simple(self):
        class A(object):
            pass

        def f(i):
            a = A()
            a.x = i
            return a.x + a.x

        self.check(f, [int], 0)

    def test_irrelevant_setfield(self):
        class A(object):
            pass

        def f(i):
            a = A()
            a.x = i
            one = a.x
            a.y = 3
            two = a.x
            return one + two

        self.check(f, [int], 0)

    def test_relevant_setfield(self):
        class A(object):
            pass

        def f(i):
            a = A()
            b = A()
            a.x = i
            b.x = i + 1
            one = a.x
            b.x = i
            two = a.x
            return one + two

        self.check(f, [int], 2)

    def test_different_concretetype(self):
        class A(object):
            pass

        class B(object):
            pass

        def f(i):
            a = A()
            b = B()
            a.x = i
            one = a.x
            b.x = i + 1
            two = a.x
            return one + two

        self.check(f, [int], 0)

    def test_subclass(self):
        class A(object):
            pass

        class B(A):
            pass

        def f(i):
            a = A()
            b = B()
            a.x = i
            one = a.x
            b.x = i + 1
            two = a.x
            return one + two

        self.check(f, [int], 1)

    def test_bug_1(self):
        class A(object):
            pass

        def f(i):
            a = A()
            a.cond = i > 0
            n = a.cond
            if a.cond:
                return True
            return n

        self.check(f, [int], 0)


    def test_cfg_splits(self):
        class A(object):
            pass

        def f(i):
            a = A()
            j = i
            for i in range(i):
                a.x = i
                if i:
                    j = a.x + a.x
                else:
                    j = a.x * 5
            return j

        self.check(f, [int], 0)

    def test_malloc_does_not_invalidate(self):
        class A(object):
            pass
        class B(object):
            pass

        def f(i):
            a = A()
            a.x = i
            b = B()
            return a.x

        self.check(f, [int], 0)

    def test_debug_assert_not_none(self):
        from rpython.rlib.debug import ll_assert_not_none
        class A(object):
            pass

        def g(i):
            if i:
                return None
            else:
                return A()

        def f(i):
            a1 = g(i)
            a = A()
            a.x = i
            ll_assert_not_none(a1)
            return a.x

        self.check(f, [int], 0)

    def test_read_none_field_bug(self):
        from rpython.translator.backendopt import inline, constfold
        class A(object):
            _immutable_fields_ = ['next']

        def g(i):
            if i == 1:
                return None
            a = A()
            a.next = 12 * i
            return a

        def f(i):
            g(i)
            a = g(1)
            return a.next

        t = self.translate(f, [int])
        graph = graphof(t, f)
        inline.auto_inline_graphs(t, [graph, graphof(t, g)], 100)
        constfold.constant_fold_graph(graph)
        removenoops.remove_same_as(graph)
        checkgraph(graph)
        storesink_graph(graph)
        checkgraph(graph)
