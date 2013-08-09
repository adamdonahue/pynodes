import nodes
import unittest

class GraphTestCase(unittest.TestCase):

    def test_graphMethod(self):
        class T(nodes.GraphEnabled):
            @nodes.graphMethod
            def f(self):
                return True

            @nodes.graphMethod()
            def g(self):
                return False

            @nodes.graphMethod(nodes.Settable)
            def h(self):
                return None

            @nodes.graphMethod
            def i(self):
                if self.f():
                    return 'Yes'

            def o(self):
                return

        self.assertIsInstance(T.f, nodes.GraphMethodDescriptor)
        self.assertIsInstance(T.g, nodes.GraphMethodDescriptor)
        self.assertIsInstance(T.h, nodes.GraphMethodDescriptor)
        self.assertIsInstance(T.i, nodes.GraphMethodDescriptor)
        self.assertNotIsInstance(T.o, nodes.GraphMethodDescriptor)

        t = T()

        self.assertIsInstance(t.f, nodes.GraphMethod)
        self.assertIsInstance(t.g, nodes.GraphMethod)
        self.assertIsInstance(t.h, nodes.GraphMethod)
        self.assertIsInstance(t.i, nodes.GraphMethod)
        self.assertNotIsInstance(t.o, nodes.GraphMethod)

    def test_simpleCalc(self):
        class SimpleCalc(nodes.GraphEnabled):
            @nodes.graphMethod
            def f(self):
                return 'f'

            @nodes.graphMethod
            def g(self):
                return '%sg' % self.f()

            def h(self):
                return '%sh' % self.f()

        simpleCalc = SimpleCalc()

        self.assertEquals(simpleCalc.f(), 'f')
        self.assertEquals(simpleCalc.g(), 'fg')
        self.assertEquals(simpleCalc.h(), 'fh')

    def test_simpleSet(self):
        class SimpleSet(nodes.GraphEnabled):
            @nodes.graphMethod
            def f(self):
                return 'f' + self.g()

            @nodes.graphMethod(nodes.Settable)
            def g(self):
                return 'g' + self.h()

            @nodes.graphMethod(nodes.Settable)
            def h(self):
                return 'h'

        s = SimpleSet()

        # FIXME: self.assertFalse(s.f.node().valid())
        # FIXME: self.assertFalse(s.g.node().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gh')
        # self.assertFalse(s.f.resolve().valid())
        # self.assertTrue(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.f(), 'fgh')
        # self.assertTrue(s.f.resolve().valid())
        # self.assertTrue(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        s.g.setValue('G')
        # self.assertFalse(s.f.resolve().valid())
        # self.assertTrue(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertTrue(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'G')
        self.assertEquals(s.f(), 'fG')
        s.g.unsetValue()
        # self.assertFalse(s.f.resolve().valid())
        # self.assertFalse(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gh')
        # self.assertFalse(s.f.resolve().valid())
        # self.assertTrue(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.f(), 'fgh')
        # self.assertTrue(s.f.resolve().valid())
        # self.assertTrue(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        s.g = 'G'
        # self.assertFalse(s.f.resolve().valid())
        # self.assertTrue(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertTrue(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'G')
        self.assertEquals(s.f(), 'fG')
        s.h = 'H'
        # self.assertTrue(s.f.resolve().valid())
        # self.assertTrue(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertTrue(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'G')
        self.assertEquals(s.f(), 'fG')
        self.assertEquals(s.h(), 'H')
        s.g.unsetValue()
        # self.assertFalse(s.f.resolve().valid())
        # self.assertFalse(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gH')
        self.assertEquals(s.f(), 'fgH')
        self.assertEquals(s.h(), 'H')
        s.h.unsetValue()
        # self.assertFalse(s.f.resolve().valid())
        # self.assertFalse(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gh')
        self.assertEquals(s.f(), 'fgh')
        self.assertEquals(s.h(), 'h')

    def test_args_consistency(self):
        class ArgsConsistency(nodes.GraphEnabled):
            @nodes.graphMethod
            def f(self):
                return

            @nodes.graphMethod
            def g(self, x):
                return

            @nodes.graphMethod
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
        class Dependencies(nodes.GraphEnabled):
            @nodes.graphMethod
            def f(self):
                return 'f' + self.g()

            @nodes.graphMethod
            def g(self):
                return 'g' + self.h()

            def h(self):
                return 'h' + self.i()

            @nodes.graphMethod
            def i(self):
                return 'i' + self.j() + self.k()

            @nodes.graphMethod
            def j(self):
                return 'j'

            @nodes.graphMethod
            def k(self):
                return 'k'

        deps = Dependencies()

        # FIXME: self.assertFalse(deps.f.resolve().valid())
        # FIXME: self.assertFalse(deps.g.resolve().valid())
        # FIXME: self.assertFalse(deps.i.resolve().valid())
        # FIXME: self.assertFalse(deps.j.resolve().valid())
        # FIXME: self.assertFalse(deps.k.resolve().valid())
        # FIXME: self.assertFalse(m.resolve().valid())
        # FIXME: self.assertFalse(n.resolve().valid())

        self.assertEquals(deps.j(), 'j')
        # FIXME: self.assertFalse(deps.f.resolve().valid())
        # FIXME: self.assertFalse(deps.g.resolve().valid())
        # FIXME: self.assertFalse(deps.i.resolve().valid())
        # FIXME: self.assertTrue(deps.j.resolve().valid())
        # FIXME: self.assertFalse(deps.k.resolve().valid())
        # FIXME: self.assertFalse(m.resolve().valid())
        # FIXME: self.assertFalse(n.resolve().valid())
        # FIXME: self.assertEquals(deps.j.resolve()._inputNodes, set())
        # FIXME: self.assertEquals(deps.j.resolve()._outputNodes, set())
        # FIXME: self.assertEquals(deps.k.resolve()._inputNodes, set())
        # self.assertEquals(deps.k.resolve()._outputNodes, set())
        # self.assertEquals(deps.i.resolve()._outputNodes, set())
        # self.assertEquals(deps.i.resolve()._inputNodes, set())
        # self.assertEquals(deps.g.resolve()._inputNodes, set([]))
        # self.assertEquals(deps.g.resolve()._outputNodes, set([]))
        # self.assertEquals(deps.f.resolve()._inputNodes, set([]))
        # self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        # self.assertEquals(m.resolve()._inputNodes, set([]))
        # self.assertEquals(m.resolve()._outputNodes, set([]))
        # self.assertEquals(n.resolve()._inputNodes, set([]))
        # self.assertEquals(n.resolve()._outputNodes, set([]))

        self.assertEquals(deps.i(), 'ijk')
        # self.assertFalse(deps.f.resolve().valid())
        # self.assertFalse(deps.g.resolve().valid())
        # self.assertTrue(deps.i.resolve().valid())
        # self.assertTrue(deps.j.resolve().valid())
        # self.assertTrue(deps.k.resolve().valid())
        # self.assertEquals(deps.j.resolve()._inputNodes, set())
        # self.assertEquals(deps.j.resolve()._outputNodes, set([deps.i.resolve()]))
        # self.assertEquals(deps.k.resolve()._inputNodes, set())
        # self.assertEquals(deps.k.resolve()._outputNodes, set([deps.i.resolve()]))
        # self.assertEquals(deps.i.resolve()._outputNodes, set())
        # self.assertEquals(deps.i.resolve()._inputNodes, set([deps.j.resolve(), deps.k.resolve()]))
        # self.assertEquals(deps.g.resolve()._inputNodes, set([]))
        # self.assertEquals(deps.g.resolve()._outputNodes, set([]))
        # self.assertEquals(deps.f.resolve()._inputNodes, set([]))
        # self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        # self.assertEquals(m.resolve()._inputNodes, set([]))
        # self.assertEquals(m.resolve()._outputNodes, set([]))
        # self.assertEquals(n.resolve()._inputNodes, set([]))
        # self.assertEquals(n.resolve()._outputNodes, set([]))

        self.assertEquals(deps.g(), 'ghijk')
        # self.assertFalse(deps.f.resolve().valid())
        # self.assertFalse(m.resolve().valid())
        # self.assertFalse(n.resolve().valid())
        # self.assertTrue(deps.g.resolve().valid())
        # self.assertTrue(deps.i.resolve().valid())
        # self.assertTrue(deps.j.resolve().valid())
        # self.assertTrue(deps.k.resolve().valid())
        # self.assertEquals(deps.j.resolve()._inputNodes, set())
        # self.assertEquals(deps.j.resolve()._outputNodes, set([deps.i.resolve()]))
        # self.assertEquals(deps.k.resolve()._inputNodes, set())
        # self.assertEquals(deps.k.resolve()._outputNodes, set([deps.i.resolve()]))
        # self.assertEquals(deps.i.resolve()._inputNodes, set([deps.j.resolve(), deps.k.resolve()]))
        # self.assertEquals(deps.i.resolve()._outputNodes, set([deps.g.resolve()]))
        # self.assertEquals(deps.g.resolve()._inputNodes, set([deps.i.resolve()]))
        # self.assertEquals(deps.g.resolve()._outputNodes, set([]))
        # self.assertEquals(deps.f.resolve()._inputNodes, set([]))
        # self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        # self.assertEquals(m.resolve()._inputNodes, set([]))
        # self.assertEquals(m.resolve()._outputNodes, set([]))
        # self.assertEquals(n.resolve()._inputNodes, set([]))
        # self.assertEquals(n.resolve()._outputNodes, set([]))

        self.assertEquals(deps.f(), 'fghijk')
        # self.assertTrue(deps.f.resolve().valid())
        # self.assertTrue(deps.g.resolve().valid())
        # self.assertTrue(deps.i.resolve().valid())
        # self.assertTrue(deps.j.resolve().valid())
        # self.assertTrue(deps.k.resolve().valid())
        # self.assertTrue(m.resolve().valid())
        # self.assertFalse(n.resolve().valid())
        # self.assertEquals(deps.j.resolve()._inputNodes, set())
        # self.assertEquals(deps.j.resolve()._outputNodes, set([deps.i.resolve()]))
        # self.assertEquals(deps.k.resolve()._inputNodes, set())
        # self.assertEquals(deps.k.resolve()._outputNodes, set([deps.i.resolve()]))
        # self.assertEquals(deps.i.resolve()._inputNodes, set([deps.j.resolve(), deps.k.resolve()]))
        # self.assertEquals(deps.i.resolve()._outputNodes, set([deps.g.resolve()]))
        # self.assertEquals(deps.g.resolve()._inputNodes, set([deps.i.resolve()]))
        # self.assertEquals(deps.g.resolve()._outputNodes, set([deps.f.resolve()]))
        # self.assertEquals(deps.f.resolve()._inputNodes, set([deps.g.resolve(), m.resolve()]))
        # self.assertEquals(deps.f.resolve()._outputNodes, set([]))
        # self.assertEquals(m.resolve()._inputNodes, set([]))
        # self.assertEquals(m.resolve()._outputNodes, set([deps.f.resolve()]))
        # self.assertEquals(n.resolve()._inputNodes, set([]))
        # self.assertEquals(n.resolve()._outputNodes, set([]))

    def test_metaclass(self):
        def makeGraphEnabledSubclass():
            class T(nodes.GraphEnabled):
                def __init__(self):
                    return
        self.assertRaises(makeGraphEnabledSubclass)

    def test_init(self):
        class InitTest(nodes.GraphEnabled):
            @nodes.graphMethod(nodes.Settable)
            def f(self):
                return None

            @nodes.graphMethod(nodes.Settable)
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
        class DictArgs(nodes.GraphEnabled):

            @nodes.graphMethod
            def fnWithDictArgs(self, arg):
                return arg

        da = DictArgs()
        da.fnWithDictArgs({})


if __name__ == '__main__':
    unittest.main()
