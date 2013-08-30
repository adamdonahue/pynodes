import nodes
import nodes.graph
import unittest

class GraphTestCase(unittest.TestCase):

    def test_graphMethod(self):
        class T(nodes.GraphObject):
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
        class SimpleCalc(nodes.GraphObject):
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
        class SimpleSet(nodes.GraphObject):
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
        s.g.clearValue()
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
        s.g.clearValue()
        # self.assertFalse(s.f.resolve().valid())
        # self.assertFalse(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gH')
        self.assertEquals(s.f(), 'fgH')
        self.assertEquals(s.h(), 'H')
        s.h.clearValue()
        # self.assertFalse(s.f.resolve().valid())
        # self.assertFalse(s.g.resolve().valid())
        # self.assertFalse(s.f.resolve().fixed())
        # self.assertFalse(s.g.resolve().fixed())
        self.assertEquals(s.g(), 'gh')
        self.assertEquals(s.f(), 'fgh')
        self.assertEquals(s.h(), 'h')

    def test_args_consistency(self):
        class ArgsConsistency(nodes.GraphObject):
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
        class Dependencies(nodes.GraphObject):
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
        def makeGraphObjectSubclass():
            class T(nodes.GraphObject):
                def __init__(self):
                    return
        self.assertRaises(makeGraphObjectSubclass)

    def test_init(self):
        class InitTest(nodes.GraphObject):
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

        i.f.clearValue()
        i.g.clearValue()
        self.assertIsNone(i.f())
        self.assertIsNone(i.g())

    def x_test_DictArgs(self):
        class DictArgs(nodes.GraphObject):

            @nodes.graphMethod
            def fnWithDictArgs(self, arg):
                return arg

        da = DictArgs()
        da.fnWithDictArgs({})

    # def test_dataStore(self):
    #     class G(nodes.GraphObject):
    #         @nodes.graphMethod(nodes.Settable)
    #         def N(self):
    #             return 0
    # 
    #     g = G()
    #   self.assertEquals(g.N(), 0)
    #   g.N = 1
    #   self.assertEquals(g.N(), 1)
    #   with nodes.graphDataStore() as ds:
    #       g.N = 2
    #       self.assertEquals(g.N(), 2)
    #   self.assertEquals(g.N(), 1)
    #   g.N.clearValue()
    #   self.assertEquals(g.N(), 0)
    #   with ds:
    #       self.assertEquals(g.N(), 2)
    #   self.assertEquals(g.N(), 0)
    #   with nodes.graphDataStore() as ds2:
    #       g.N = 3
    #       self.assertEquals(g.N(), 3)
    #   self.assertEquals(g.N(), 0)
    #   g.N = 1
    #   self.assertEquals(g.N(), 1)
    #   with ds:
    #       self.assertEquals(g.N(), 2)
    #   with ds2:
    #       self.assertEquals(g.N(), 3)
    #   with ds:
    #       with ds2:
    #           self.assertEquals(g.N(), 3)
    #       self.assertEquals(g.N(), 2)
    #   self.assertEquals(g.N(), 1)
    #   g.N.clearValue()
    #   self.assertEquals(g.N(), 0)
    #   with ds:
    #       with ds2:
    #           self.assertEquals(g.N(), 3)
    #           g.N.clearValue()
    #           self.assertEquals(g.N(), 2)
    #       self.assertEquals(g.N(), 2)
    #   self.assertEquals(g.N(), 0)
    #
    #   with ds2:
    #       self.assertEquals(g.N(), 0)
    #       with ds:
    #           self.assertEquals(g.N(), 2)
    #       self.assertEquals(g.N(), 0)
    #       with ds:
    #           self.assertEquals(g.N(), 2)

    def test_scenario(self):
        class ScenarioTest(nodes.GraphObject):

            @nodes.graphMethod
            def X(self):
                return self.Y() + self.Z()

            @nodes.graphMethod(nodes.Settable)
            def Y(self):
                return 'y'

            @nodes.graphMethod(nodes.Settable)
            def Z(self):
                return 'z'

        st1 = ScenarioTest()
        st2 = ScenarioTest(Y='y2', Z='z2')

        self.assertEquals(st1.X(), 'yz')
        self.assertEquals(st2.X(), 'y2z2')

        with nodes.scenario():
            self.assertEquals(st1.X(), 'yz')
            self.assertEquals(st2.X(), 'y2z2')

            # Setting Y should cause a set in the root data store,
            # not this scenario.  Still, the scenario should pick
            # up the changed root store value.
            st1.Y = 'y1'
            self.assertEquals(st1.Y(), 'y1')
            self.assertEquals(st1.X(), 'y1z')
            self.assertEquals(st2.X(), 'y2z2')

        self.assertEquals(st1.X(), 'y1z')
        self.assertEquals(st1.Y(), 'y1')

        with nodes.scenario():
            self.assertEquals(st1.X(), 'y1z')
            self.assertEquals(st2.X(), 'y2z2')

            st1.Y.clearValue()
            self.assertEquals(st1.X(), 'yz')
            self.assertEquals(st2.X(), 'y2z2')

        self.assertEquals(st1.X(), 'yz')
        self.assertEquals(st2.X(), 'y2z2')

        with nodes.scenario() as s:
            st1.Y.setWhatIf('y2')
            self.assertEquals(st1.Y(), 'y2')
            self.assertEquals(st1.X(), 'y2z')
            whatIfs = s.whatIfs()

        self.assertEquals(whatIfs, s.whatIfs())
        self.assertEquals(st1.Y(), 'y')
        self.assertEquals(st1.X(), 'yz')
        self.assertEquals(st2.X(), 'y2z2')

        with s:
            self.assertEquals(st1.Y(), 'y2')
            self.assertEquals(st1.X(), 'y2z')
            self.assertEquals(st2.X(), 'y2z2')
        self.assertEquals(whatIfs, s.whatIfs())
        self.assertEquals(st1.Y(), 'y')
        self.assertEquals(st1.X(), 'yz')
        self.assertEquals(st2.X(), 'y2z2')

        with nodes.scenario() as s2:
            self.assertEquals(st1.Y(), 'y')
            st1.Y.setWhatIf('y3')
            self.assertEquals(st1.Y(), 'y3')
            self.assertEquals(st1.X(), 'y3z')
            with s:
                self.assertEquals(st1.Y(), 'y2')
                self.assertEquals(st1.X(), 'y2z')
            self.assertEquals(st1.Y(), 'y3')
            self.assertEquals(st1.X(), 'y3z')
        self.assertEquals(st1.X(), 'yz')
        with s:
            self.assertEquals(st1.X(), 'y2z')
            with s2:
                self.assertEquals(st1.X(), 'y3z')
            self.assertEquals(st1.Y(), 'y2')
            self.assertEquals(st1.X(), 'y2z')

            st1.Y.clearWhatIf()
            self.assertEquals(st1.X(), 'yz')
            with s2:
                self.assertEquals(st1.X(), 'y3z')
            self.assertEquals(st1.Y(), 'y')
        with s:
            self.assertEquals(st1.X(), 'yz')
        with s2:
            self.assertEquals(st1.X(), 'y3z')

        st1.Y = 'q'
        self.assertEquals(st1.X(), 'qz')
        with s:
            self.assertEquals(st1.X(), 'qz')
        with s2:
            self.assertEquals(st1.X(), 'y3z')
        self.assertEquals(st1.X(), 'qz')
        st1.Z = 't'
        self.assertEquals(st1.X(), 'qt')
        with s:
            self.assertEquals(st1.X(), 'qt')
            st1.Y.setWhatIf('q2')
            self.assertEquals(st1.X(), 'q2t')
            st1.Z.setWhatIf('t2')
            self.assertEquals(st1.X(), 'q2t2')
            with s2:
                self.assertEquals(st1.X(), 'y3t2')
            self.assertEquals(st1.X(), 'q2t2')
            with s2:
                self.assertEquals(st1.X(), 'y3t2')
                st2.Y = 'Y'
                self.assertEquals(st1.X(), 'y3t2')
                self.assertEquals(st2.X(), 'Yz2')
                st2.Y.setWhatIf('YYY')
                self.assertEquals(st2.X(), 'YYYz2')
                st2.Z.setWhatIf('Z')
                self.assertEquals(st2.X(), 'YYYZ')
                st2.Y.clearWhatIf()
                self.assertEquals(st2.X(), 'YZ')
                st1.Y = 'Y'
            self.assertEquals(st2.X(), 'Yz2')
            self.assertEquals(st1.X(), 'q2t2')
            st1.Y.clearWhatIf()
            self.assertEquals(st1.X(), 'Yt2')
        self.assertEquals(st1.X(), 'Yt')
        self.assertEquals(st2.X(), 'Yz2')
        with s2:
            self.assertEquals(st1.X(), 'y3t')
            self.assertEquals(st1.Y(), 'y3')
            self.assertEquals(st1.Z(), 't')
            with s:
                self.assertEquals(st1.X(), 'y3t2')
            self.assertEquals(st1.X(), 'y3t')
            self.assertEquals(st1.Y(), 'y3')
            self.assertEquals(st1.Z(), 't')
        self.assertEquals(st1.Y(), 'Y')
        self.assertEquals(st1.X(), 'Yt')
        st1.Y.clearValue()
        self.assertEquals(st1.X(), 'yt')
        self.assertEquals(st1.Y(), 'y')
        st1.Z.clearValue()
        self.assertEquals(st1.Y(), 'y')
        self.assertEquals(st1.Z(), 'z')
        self.assertEquals(st1.X(), 'yz')
        self.assertEquals(st2.Y(), 'Y')
        st2.Y.clearValue()
        self.assertEquals(st2.Y(), 'y')
        self.assertEquals(st2.X(), 'yz2')
        st2.Z.clearValue()
        self.assertEquals(st2.X(), 'yz')

if __name__ == '__main__':
    unittest.main()
