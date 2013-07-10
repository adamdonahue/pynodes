import nodes.graph as graph
import unittest

class GraphTestCase(unittest.TestCase):

    def test_graphEnabled(self):
        class T(graph.GraphEnabled):
            @graph.graphEnabled
            def f(self):
                return True

            @graph.graphEnabled()
            def g(self):
                return False

            @graph.graphEnabled(graph.SETTABLE)
            def h(self):
                return None

            @graph.graphEnabled
            def i(self):
                if self.f():
                    return 'Yes'

            def o(self):
                return

        self.assertIsInstance(T.f, graph.GraphEnabledFunction)
        self.assertIsInstance(T.g, graph.GraphEnabledFunction)
        self.assertIsInstance(T.h, graph.GraphEnabledFunction)
        self.assertIsInstance(T.i, graph.GraphEnabledFunction)
        self.assertNotIsInstance(T.o, graph.GraphEnabledFunction)

        t = T()

        self.assertIsInstance(t.f, graph.GraphEnabledMethod)
        self.assertIsInstance(t.g, graph.GraphEnabledMethod)
        self.assertIsInstance(t.h, graph.GraphEnabledMethod)
        self.assertIsInstance(t.i, graph.GraphEnabledMethod)
        self.assertNotIsInstance(t.o, graph.GraphEnabledMethod)

    def test_simpleCalc(self):
        class SimpleCalc(graph.GraphEnabled):
            @graph.graphEnabled
            def f(self):
                return 'f'

            @graph.graphEnabled
            def g(self):
                return '%sg' % self.f()

            def h(self):
                return '%sh' % self.f()

        simpleCalc = SimpleCalc()

        self.assertEquals(simpleCalc.f(), 'f')
        self.assertEquals(simpleCalc.g(), 'fg')
        self.assertEquals(simpleCalc.h(), 'fh')

    def test_simpleSet(self):
        class SimpleSet(graph.GraphEnabled):
            @graph.graphEnabled
            def f(self):
                return 'f' + self.g()

            @graph.graphEnabled(graph.SETTABLE)
            def g(self):
                return 'g' + self.h()

            @graph.graphEnabled(graph.SETTABLE)
            def h(self):
                return 'h'

        s = SimpleSet()

        self.assertFalse(s.f.resolve().valid())
        self.assertFalse(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gh')
        self.assertFalse(s.f.resolve().valid())
        self.assertTrue(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.f(), 'fgh')
        self.assertTrue(s.f.resolve().valid())
        self.assertTrue(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertFalse(s.g.resolve().fixed())
        s.g.setValue('G')
        self.assertFalse(s.f.resolve().valid())
        self.assertTrue(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertTrue(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'G')
        self.assertEquals(s.f(), 'fG')
        s.g.unsetValue()
        self.assertFalse(s.f.resolve().valid())
        self.assertFalse(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gh')
        self.assertFalse(s.f.resolve().valid())
        self.assertTrue(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.f(), 'fgh')
        self.assertTrue(s.f.resolve().valid())
        self.assertTrue(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertFalse(s.g.resolve().fixed())
        s.g = 'G'
        self.assertFalse(s.f.resolve().valid())
        self.assertTrue(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertTrue(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'G')
        self.assertEquals(s.f(), 'fG')
        s.h = 'H'
        self.assertTrue(s.f.resolve().valid())
        self.assertTrue(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertTrue(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'G')
        self.assertEquals(s.f(), 'fG')
        self.assertEquals(s.h(), 'H')
        s.g.unsetValue()
        self.assertFalse(s.f.resolve().valid())
        self.assertFalse(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gH')
        self.assertEquals(s.f(), 'fgH')
        self.assertEquals(s.h(), 'H')
        s.h.unsetValue()
        self.assertFalse(s.f.resolve().valid())
        self.assertFalse(s.g.resolve().valid())
        self.assertFalse(s.f.resolve().fixed())
        self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gh')
        self.assertEquals(s.f(), 'fgh')
        self.assertEquals(s.h(), 'h')

    def test_args_consistency(self):
        class ArgsConsistency(graph.GraphEnabled):
            @graph.graphEnabled
            def f(self):
                return

            @graph.graphEnabled
            def g(self, x):
                return

            @graph.graphEnabled
            def h(self, x, y, *args):
                return

        ac = ArgsConsistency()
        ac.f()
        # SHOULD FAIL: ac.f(None)
        # SHOULD FAIL: ac.g()
        ac.g(None)
        # SHOULD FAIL: ac.g(None, None)
        # SHOULD FAIL: ac.h()
        # SHOULD FAIL: ac.h(None)
        ac.h(None, None)
        ac.h(None, None, None)
        ac.h(*[None,None])
        ac.h(*[None,None,None])

    def test_dependencies(self):
        class Dependencies(graph.GraphEnabled):
            @graph.graphEnabled
            def f(self):
                return 'f' + self.g() + m()

            @graph.graphEnabled
            def g(self):
                return 'g' + self.h()

            def h(self):
                return 'h' + self.i()

            @graph.graphEnabled
            def i(self):
                return 'i' + self.j() + self.k()

            @graph.graphEnabled
            def j(self):
                return 'j'

            @graph.graphEnabled
            def k(self):
                return 'k'

        @graph.graphEnabled
        def m():
            return 'm'

        @graph.graphEnabled
        def n():
            return m()

        deps = Dependencies()

        self.assertFalse(deps.f.resolve().valid())
        self.assertFalse(deps.g.resolve().valid())
        self.assertFalse(deps.i.resolve().valid())
        self.assertFalse(deps.j.resolve().valid())
        self.assertFalse(deps.k.resolve().valid())
        self.assertFalse(m.resolve().valid())
        self.assertFalse(n.resolve().valid())

        self.assertEquals(deps.j(), 'j')
        self.assertFalse(deps.f.resolve().valid())
        self.assertFalse(deps.g.resolve().valid())
        self.assertFalse(deps.i.resolve().valid())
        self.assertTrue(deps.j.resolve().valid())
        self.assertFalse(deps.k.resolve().valid())
        self.assertFalse(m.resolve().valid())
        self.assertFalse(n.resolve().valid())
        self.assertEquals(deps.j.resolve()._inputNodes, set())
        self.assertEquals(deps.j.resolve()._outputNodes, set())
        self.assertEquals(deps.k.resolve()._inputNodes, set())
        self.assertEquals(deps.k.resolve()._outputNodes, set())
        self.assertEquals(deps.i.resolve()._outputNodes, set())
        self.assertEquals(deps.i.resolve()._inputNodes, set())
        self.assertEquals(deps.g.resolve()._inputNodes, set([]))
        self.assertEquals(deps.g.resolve()._outputNodes, set([]))
        self.assertEquals(deps.f.resolve()._inputNodes, set([]))
        self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        self.assertEquals(m.resolve()._inputNodes, set([]))
        self.assertEquals(m.resolve()._outputNodes, set([]))
        self.assertEquals(n.resolve()._inputNodes, set([]))
        self.assertEquals(n.resolve()._outputNodes, set([]))

        self.assertEquals(deps.i(), 'ijk')
        self.assertFalse(deps.f.resolve().valid())
        self.assertFalse(deps.g.resolve().valid())
        self.assertTrue(deps.i.resolve().valid())
        self.assertTrue(deps.j.resolve().valid())
        self.assertTrue(deps.k.resolve().valid())
        self.assertEquals(deps.j.resolve()._inputNodes, set())
        self.assertEquals(deps.j.resolve()._outputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.k.resolve()._inputNodes, set())
        self.assertEquals(deps.k.resolve()._outputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.i.resolve()._outputNodes, set())
        self.assertEquals(deps.i.resolve()._inputNodes, set([deps.j.resolve(), deps.k.resolve()]))
        self.assertEquals(deps.g.resolve()._inputNodes, set([]))
        self.assertEquals(deps.g.resolve()._outputNodes, set([]))
        self.assertEquals(deps.f.resolve()._inputNodes, set([]))
        self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        self.assertEquals(m.resolve()._inputNodes, set([]))
        self.assertEquals(m.resolve()._outputNodes, set([]))
        self.assertEquals(n.resolve()._inputNodes, set([]))
        self.assertEquals(n.resolve()._outputNodes, set([]))

        self.assertEquals(deps.g(), 'ghijk')
        self.assertFalse(deps.f.resolve().valid())
        self.assertFalse(m.resolve().valid())
        self.assertFalse(n.resolve().valid())
        self.assertTrue(deps.g.resolve().valid())
        self.assertTrue(deps.i.resolve().valid())
        self.assertTrue(deps.j.resolve().valid())
        self.assertTrue(deps.k.resolve().valid())
        self.assertEquals(deps.j.resolve()._inputNodes, set())
        self.assertEquals(deps.j.resolve()._outputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.k.resolve()._inputNodes, set())
        self.assertEquals(deps.k.resolve()._outputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.i.resolve()._inputNodes, set([deps.j.resolve(), deps.k.resolve()]))
        self.assertEquals(deps.i.resolve()._outputNodes, set([deps.g.resolve()]))
        self.assertEquals(deps.g.resolve()._inputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.g.resolve()._outputNodes, set([]))
        self.assertEquals(deps.f.resolve()._inputNodes, set([]))
        self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        self.assertEquals(m.resolve()._inputNodes, set([]))
        self.assertEquals(m.resolve()._outputNodes, set([]))
        self.assertEquals(n.resolve()._inputNodes, set([]))
        self.assertEquals(n.resolve()._outputNodes, set([]))

        self.assertEquals(deps.f(), 'fghijkm')
        self.assertTrue(deps.f.resolve().valid())
        self.assertTrue(deps.g.resolve().valid())
        self.assertTrue(deps.i.resolve().valid())
        self.assertTrue(deps.j.resolve().valid())
        self.assertTrue(deps.k.resolve().valid())
        self.assertTrue(m.resolve().valid())
        self.assertFalse(n.resolve().valid())
        self.assertEquals(deps.j.resolve()._inputNodes, set())
        self.assertEquals(deps.j.resolve()._outputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.k.resolve()._inputNodes, set())
        self.assertEquals(deps.k.resolve()._outputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.i.resolve()._inputNodes, set([deps.j.resolve(), deps.k.resolve()]))
        self.assertEquals(deps.i.resolve()._outputNodes, set([deps.g.resolve()]))
        self.assertEquals(deps.g.resolve()._inputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.g.resolve()._outputNodes, set([deps.f.resolve()]))
        self.assertEquals(deps.f.resolve()._inputNodes, set([deps.g.resolve(), m.resolve()]))
        self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        self.assertEquals(m.resolve()._inputNodes, set([]))
        self.assertEquals(m.resolve()._outputNodes, set([deps.f.resolve()]))
        self.assertEquals(n.resolve()._inputNodes, set([]))
        self.assertEquals(n.resolve()._outputNodes, set([]))

        self.assertEquals(n(), 'm')
        self.assertTrue(deps.f.resolve().valid())
        self.assertTrue(deps.g.resolve().valid())
        self.assertTrue(deps.i.resolve().valid())
        self.assertTrue(deps.j.resolve().valid())
        self.assertTrue(deps.k.resolve().valid())
        self.assertTrue(m.resolve().valid())
        self.assertTrue(n.resolve().valid())
        self.assertEquals(deps.j.resolve()._inputNodes, set())
        self.assertEquals(deps.j.resolve()._outputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.k.resolve()._inputNodes, set())
        self.assertEquals(deps.k.resolve()._outputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.i.resolve()._inputNodes, set([deps.j.resolve(), deps.k.resolve()]))
        self.assertEquals(deps.i.resolve()._outputNodes, set([deps.g.resolve()]))
        self.assertEquals(deps.g.resolve()._inputNodes, set([deps.i.resolve()]))
        self.assertEquals(deps.g.resolve()._outputNodes, set([deps.f.resolve()]))
        self.assertEquals(deps.f.resolve()._inputNodes, set([deps.g.resolve(), m.resolve()]))
        self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        self.assertEquals(m.resolve()._inputNodes, set([]))
        self.assertEquals(m.resolve()._outputNodes, set([n.resolve(), deps.f.resolve()]))
        self.assertEquals(n.resolve()._inputNodes, set([m.resolve()]))
        self.assertEquals(n.resolve()._outputNodes, set([]))

    def test_metaclass(self):
        def makeGraphEnabledSubclass():
            class T(graph.GraphEnabled):
                def __init__(self):
                    return
        self.assertRaises(makeGraphEnabledSubclass)

    def test_init(self):
        class InitTest(graph.GraphEnabled):
            @graph.graphEnabled(graph.SETTABLE)
            def f(self):
                return None

            @graph.graphEnabled(graph.SETTABLE)
            def g(self):
                return None

        i = InitTest()
        self.assertIsNone(i.f())
        self.assertIsNone(i.g())

        i = InitTest(f='x')
        self.assertEquals(i.f(), 'x')
        self.assertIsNone(i.g())

        i = InitTest(f='x', g='y')
        self.assertEquals(i.f(), 'x')
        self.assertEquals(i.g(), 'y')

        i.f.unsetValue()
        i.g.unsetValue()
        self.assertIsNone(i.f())
        self.assertIsNone(i.g())

    def x_test_DictArgs(self):
        class DictArgs(graph.GraphEnabled):

            @graph.graphEnabled
            def fnWithDictArgs(self, arg):
                return arg

        da = DictArgs()
        da.fnWithDictArgs({})


if __name__ == '__main__':
    unittest.main()
