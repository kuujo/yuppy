import unittest
from yuppy import *

@encapsulate
class Constant(object):
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
    Constant.foo = 'baz'
    instance = Constant()
    self.assertEquals(instance.foo, 'bar')

@encapsulate
class PublicVariable(object):
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

@encapsulate
class PublicMethod(object):
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

@encapsulate
class PublicStaticVariable(object):
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

@encapsulate
class PublicStaticMethod(object):
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
    self.assertEquals(instance.foo(), instance.__private__.__class__)

@encapsulate
class ProtectedVariable(object):
  foo = protected(type=int, validate=lambda x: x == 1)
  @public
  def setfoo(self, value):
    self.foo = value
  @public
  def getfoo(self):
    return self.foo

@encapsulate
class ExtendedVariable(ProtectedVariable):
  @public
  def extfoo(self):
    return self.foo

class ProtectedVariableTestCase(unittest.TestCase):
  """
  Protected member variable test case.
  """
  def test_protected_variable(self):
    instance = ProtectedVariable()
    def getfoo():
      instance.foo
    def setfoo(value):
      instance.foo = value
    self.assertRaises(AttributeError, getfoo)
    self.assertRaises(AttributeError, setfoo, 2)
    instance.setfoo(1)
    self.assertEquals(instance.getfoo(), 1)
    instance2 = ExtendedVariable()
    def getfoo():
      instance2.foo
    def setfoo(value):
      instance2.foo = value
    self.assertRaises(AttributeError, getfoo)
    self.assertRaises(AttributeError, setfoo, 'foo')
    instance2.extfoo() # This fails!

@encapsulate
class ProtectedMethod(object):
  @protected
  def foo(self):
    return 'bar'
  def getfoo(self):
    return self.foo()

@encapsulate
class ExtendedMethod(ProtectedMethod):
  @public
  def extfoo(self):
    return self.foo()

class ProtectedMethodTestCase(unittest.TestCase):
  """
  Protected method test case.
  """
  def test_protected_method(self):
    instance = ExtendedMethod()
    def getfoo():
      instance.foo
    self.assertRaises(AttributeError, getfoo)
    instance.getfoo()
    instance.extfoo()

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

@encapsulate
class PrivateVariable(object):
  foo = private(type=int, validate=lambda x: x == 1)
  def setfoo(self, value):
    self.foo = value
  def getfoo(self):
    return self.foo

class PrivateVariableTestCase(unittest.TestCase):
  """
  Private member variable test case.
  """
  def test_private_variable(self):
    instance = PrivateVariable()
    def getfoo(value):
      instance.foo
    def setfoo(value):
      instance.foo = value
    self.assertRaises(AttributeError, setfoo, 'foo')
    self.assertRaises(AttributeError, setfoo, 2)
    instance.setfoo(1)
    self.assertEquals(instance.getfoo(), 1)

@encapsulate
class PrivateMethod(object):
  @private
  def foo(self):
    return 'bar'
  def getfoo(self):
    return self.foo()

class PrivateMethodTestCase(unittest.TestCase):
  """
  Private method test case.
  """
  def test_private_method(self):
    instance = PrivateMethod()
    def getfoo():
      instance.foo
    self.assertRaises(AttributeError, getfoo)
    instance.getfoo()

@encapsulate
class PrivateStaticVariable(object):
  foo = static(private(type=int, validate=lambda x: x == 1))

class PrivateStaticVariableTestCase(unittest.TestCase):
  """
  Private static variable test case.
  """
  def test_public_static_variable(self):
    instance = PrivateStaticVariable()
    self.assertRaises(AttributeError, getattr, instance, 'foo')
    def setfoo(value):
      instance.foo = value
    self.assertRaises(AttributeError, setfoo, 'foo')
    self.assertRaises(AttributeError, setfoo, 2)

@encapsulate
class PrivateStaticMethod(object):
  @static
  @private
  def foo(self):
    return self

class PrivateStaticMethodTestCase(unittest.TestCase):
  """
  Private static method test case.
  """
  def test_private_static_method(self):
    instance = PrivateStaticMethod()
    self.assertRaises(AttributeError, getattr, instance, 'foo')

class PrivateConstantTestCase(unittest.TestCase):
  """
  Private constant test case.
  """

def all_tests():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(ConstantTestCase))
  suite.addTest(unittest.makeSuite(PublicVariableTestCase))
  suite.addTest(unittest.makeSuite(PublicMethodTestCase))
  suite.addTest(unittest.makeSuite(PublicStaticVariableTestCase))
  suite.addTest(unittest.makeSuite(PublicStaticMethodTestCase))
  suite.addTest(unittest.makeSuite(ProtectedVariableTestCase))
  suite.addTest(unittest.makeSuite(ProtectedMethodTestCase))
  suite.addTest(unittest.makeSuite(ProtectedStaticVariableTestCase))
  suite.addTest(unittest.makeSuite(ProtectedStaticMethodTestCase))
  suite.addTest(unittest.makeSuite(PrivateVariableTestCase))
  suite.addTest(unittest.makeSuite(PrivateMethodTestCase))
  suite.addTest(unittest.makeSuite(PrivateStaticVariableTestCase))
  suite.addTest(unittest.makeSuite(PrivateStaticMethodTestCase))
  return suite
