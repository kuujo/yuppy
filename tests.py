import unittest
from yuppy import *

class Constant(Object):
  foo = const('bar')

class ConstantTestCase(unittest.TestCase):
  """
  Constant test case.
  """
  def test_constant(self):
    def setfoo(obj, value):
      obj.foo = value
    instance = Constant()
    self.assertRaises(AttributeError, setfoo, instance, 'baz')
    self.assertEquals(instance.foo, 'bar')
    # Ensure that even after changing the class constant, the object
    # constant does not change.
    self.assertRaises(AttributeError, setfoo, Constant, 'baz')
    instance = Constant()
    self.assertEquals(instance.foo, 'bar')

class Variable(Object):
  foo = var(default=2, type=int, validate=lambda x: x == 1)

class VariableTestCase(unittest.TestCase):
  """
  Member variable test case.
  """
  def test_variable(self):
    instance = Variable()
    self.assertEquals(instance.foo, 2)
    def setfoo(value):
      instance.foo = value
    self.assertRaises(AttributeError, setfoo, 'foo')
    self.assertRaises(AttributeError, setfoo, 2)
    setfoo(1)

class Method(Object):
  @method
  def foo(self):
    return 'bar'

class MethodTestCase(unittest.TestCase):
  """
  Method test case.
  """
  def test_method(self):
    instance = Method()
    self.assertEquals(instance.foo(), 'bar')

class StaticVariable(Object):
  foo = static(type=int, validate=lambda x: x == 1)

class StaticVariableTestCase(unittest.TestCase):
  """
  Static variable test case.
  """
  def test_static_variable(self):
    instance = StaticVariable()
    self.assertRaises(AttributeError, getattr, instance, 'foo')
    def setfoo(value):
      instance.foo = value
    self.assertRaises(AttributeError, setfoo, 'foo')
    self.assertRaises(AttributeError, setfoo, 2)
    setfoo(1)
    instance2 = StaticVariable()
    self.assertEquals(instance2.foo, 1)

@final
class Foo(Object):
  """A final class."""

class FinalTestCase(unittest.TestCase):
  """
  Final test case.
  """
  def test_final(self):
    def extend_final():
      class Bar(Foo):
        pass
    foo = Foo()
    self.assertRaises(TypeError, extend_final)

class FooInterface(Interface):
  def foo(self):
    pass
  def bar(self):
    pass
  def baz(self):
    pass

class InterfaceTestCase(unittest.TestCase):
  """
  Interface test case.
  """
  def test_implements(self):
    def bad_implement():
      @implements(FooInterface)
      class FooInterfaceObject(object):
        pass
    self.assertRaises(TypeError, bad_implement)
    def good_implement():
      @implements(FooInterface)
      class FooInterfaceObject(object):
        def foo(self):
          pass
        def bar(self):
          pass
        def baz(self):
          pass
    good_implement()

  def test_good_instanceof(self):
    def implement():
      @implements(FooInterface)
      class FooInterfaceObject(object):
        def foo(self):
          pass
        def bar(self):
          pass
        def baz(self):
          pass
      return FooInterfaceObject()
    instance = implement()
    self.assertTrue(instanceof(instance, FooInterface, True))
    self.assertTrue(instanceof(instance, FooInterface, False))

  def test_bad_instanceof(self):
    def implement():
      class FooInterfaceObject(object):
        def bar(self):
          pass
        def baz(self):
          pass
      return FooInterfaceObject()
    instance = implement()
    self.assertFalse(instanceof(instance, FooInterface, False))

def all_tests():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(ConstantTestCase))
  suite.addTest(unittest.makeSuite(VariableTestCase))
  suite.addTest(unittest.makeSuite(MethodTestCase))
  suite.addTest(unittest.makeSuite(StaticVariableTestCase))
  suite.addTest(unittest.makeSuite(FinalTestCase))
  suite.addTest(unittest.makeSuite(InterfaceTestCase))
  return suite
