import unittest
from xpy import *

class PublicVariable(Object):
  foo = public(default=2, type=int, validate=lambda x: x == 1)

class PublicVariableTestCase(unittest.TestCase):
  """
  Public member variable test case.
  """
  def test_public_variable(self):
    instance = PublicVariable()
    self.assertEquals(instance.foo, 2)
    def setfoo(value):
      instance.foo = value
    self.assertRaises(AttributeError, setfoo, 'foo')
    self.assertRaises(AttributeError, setfoo, 2)
    setfoo(1)

class PublicMethod(Object):
  @public
  def foo(self):
    return 'bar'

class PublicMethodTestCase(unittest.TestCase):
  """
  Public method test case.
  """
  def test_public_method(self):
    instance = PublicMethod()
    self.assertEquals(instance.foo(), 'bar')

class PublicStaticVariable(Object):
  foo = static(public(type=int, validate=lambda x: x == 1))

class PublicStaticVariableTestCase(unittest.TestCase):
  """
  Public static variable test case.
  """
  def test_public_static_variable(self):
    instance = PublicStaticVariable()
    self.assertRaises(AttributeError, getattr, instance, 'foo')
    def setfoo(value):
      instance.foo = value
    self.assertRaises(AttributeError, setfoo, 'foo')
    self.assertRaises(AttributeError, setfoo, 2)
    setfoo(1)
    instance2 = PublicStaticVariable()
    self.assertEquals(instance2.foo, 1)

class PublicStaticMethod(Object):
  @static
  @public
  def foo(self):
    return self

class PublicStaticMethodTestCase(unittest.TestCase):
  """
  Public static method test case.
  """
  def test_public_static_method(self):
    instance = PublicStaticMethod()
    self.assertEquals(instance.foo(), instance.__class__)

class PublicConstant(Object):
  foo = const('bar')

class PublicConstantTestCase(unittest.TestCase):
  """
  Public constant test case.
  """
  def test_public_constant(self):
    PublicConstant.foo
    def setfoo(value):
      PublicConstant.foo = value
    self.assertRaises(AttributeError, setfoo, 'baz')

class ProtectedVariable(Object):
  foo = protected(type=int, validate=lambda x: x == 1)
  def setfoo(self, value):
    self.foo = value
  def getfoo(self):
    return self.foo

class ProtectedVariableTestCase(unittest.TestCase):
  """
  Protected member variable test case.
  """
  def test_protected_variable(self):
    instance = ProtectedVariable()
    def getfoo(value):
      instance.foo
    def setfoo(value):
      instance.foo = value
    self.assertRaises(AttributeError, setfoo, 'foo')
    self.assertRaises(AttributeError, setfoo, 2)
    instance.setfoo(1)
    self.assertEquals(instance.getfoo(), 1)

class ProtectedMethod(Object):
  @protected
  def foo(self):
    return 'bar'
  def getfoo(self):
    return self.foo()

class ProtectedMethodTestCase(unittest.TestCase):
  """
  Protected method test case.
  """
  def test_protected_method(self):
    instance = ProtectedMethod()
    self.assertRaises(AttributeError, instance.foo)
    instance.getfoo()

class ProtectedStaticVariableTestCase(unittest.TestCase):
  """
  Protected static variable test case.
  """

class ProtectedStaticMethodTestCase(unittest.TestCase):
  """
  Protected static method test case.
  """

class ProtectedConstantTestCase(unittest.TestCase):
  """
  Protected constant test case.
  """

class PrivateVariableTestCase(unittest.TestCase):
  """
  Private member variable test case.
  """

class PrivateMethodTestCase(unittest.TestCase):
  """
  Private method test case.
  """

class PrivateStaticVariableTestCase(unittest.TestCase):
  """
  Private static variable test case.
  """

class PrivateStaticMethodTestCase(unittest.TestCase):
  """
  Private static method test case.
  """

class PrivateConstantTestCase(unittest.TestCase):
  """
  Private constant test case.
  """

def all_tests():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(PublicVariableTestCase))
  suite.addTest(unittest.makeSuite(PublicMethodTestCase))
  suite.addTest(unittest.makeSuite(PublicStaticVariableTestCase))
  suite.addTest(unittest.makeSuite(PublicStaticMethodTestCase))
  suite.addTest(unittest.makeSuite(PublicConstantTestCase))
  suite.addTest(unittest.makeSuite(ProtectedVariableTestCase))
  suite.addTest(unittest.makeSuite(ProtectedMethodTestCase))
  suite.addTest(unittest.makeSuite(ProtectedStaticVariableTestCase))
  suite.addTest(unittest.makeSuite(ProtectedStaticMethodTestCase))
  suite.addTest(unittest.makeSuite(ProtectedConstantTestCase))
  suite.addTest(unittest.makeSuite(PrivateVariableTestCase))
  suite.addTest(unittest.makeSuite(PrivateMethodTestCase))
  suite.addTest(unittest.makeSuite(PrivateStaticVariableTestCase))
  suite.addTest(unittest.makeSuite(PrivateStaticMethodTestCase))
  suite.addTest(unittest.makeSuite(PrivateConstantTestCase))
  return suite
