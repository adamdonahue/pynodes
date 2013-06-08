import nodes.graph as graph
import unittest

class GraphTestCase(unittest.TestCase):

    def test_deferredNode(self):
        class T(graph.GraphObject): 
            @graph.deferredNode
            def f(self):
                return True

            @graph.deferredNode()
            def g(self):
                return False

            @graph.deferredNode(graph.SETTABLE)
            def h(self):
                return None

            @graph.deferredNode
            def i(self):
                if self.f():
                    return 'Yes'

        self.assertIsInstance(T.f, graph.DeferredNode)

        self.assertFalse(T.f.isBound())
        self.assertFalse(T.g.isBound())
        self.assertFalse(T.h.isBound())

        t = T()

        self.assertTrue(t.f.isBound())
        self.assertTrue(t.g.isBound())
        self.assertTrue(t.h.isBound())

    def test_simpleCalc(self):
        class SimpleCalc(graph.GraphObject):
            @graph.deferredNode
            def f(self):
                return 'f'

            @graph.deferredNode
            def g(self):
                return '%sg' % self.f()

            def h(self):
                return '%sh' % self.f()

        simpleCalc = SimpleCalc()

        self.assertEquals(simpleCalc.f(), 'f')
        self.assertEquals(simpleCalc.g(), 'fg')
        self.assertEquals(simpleCalc.h(), 'fh')

    def test_simpleSet(self):
        class SimpleSet(graph.GraphObject):
            @graph.deferredNode
            def f(self):
                return 'f' + self.g()

            @graph.deferredNode(graph.SETTABLE)
            def g(self):
                return 'g' + self.h()

            @graph.deferredNode(graph.SETTABLE)
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
        class ArgsConsistency(graph.GraphObject):
            @graph.deferredNode
            def f(self):
                return

            @graph.deferredNode
            def g(self, x):
                return

            @graph.deferredNode
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
        class Dependencies(graph.GraphObject):
            @graph.deferredNode
            def f(self):
                return 'f' + self.g() + m()

            @graph.deferredNode
            def g(self):
                return 'g' + self.h()

            def h(self):
                return 'h' + self.i()

            @graph.deferredNode
            def i(self):
                return 'i' + self.j() + self.k()

            @graph.deferredNode
            def j(self):
                return 'j'

            @graph.deferredNode
            def k(self):
                return 'k'

        @graph.deferredNode
        def m():
            return 'm'

        @graph.deferredNode
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


if __name__ == '__main__':
    unittest.main()
