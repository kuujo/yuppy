import unittest

class PublicVariableTestCase(unittest.TestCase):
  """
  Public member variable test case.
  """

class PublicMethodTestCase(unittest.TestCase):
  """
  Public method test case.
  """

class PublicStaticVariableTestCase(unittest.TestCase):
  """
  Public static variable test case.
  """

class PublicStaticMethodTestCase(unittest.TestCase):
  """
  Public static method test case.
  """

class PublicConstantTestCase(unittest.TestCase):
  """
  Public constant test case.
  """

class ProtectedVariableTestCase(unittest.TestCase):
  """
  Protected member variable test case.
  """

class ProtectedMethodTestCase(unittest.TestCase):
  """
  Protected method test case.
  """

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
