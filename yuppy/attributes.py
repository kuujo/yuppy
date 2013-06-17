# Copyright (c) 2013 Jordan Halterman
# See LICENSE for details.

class _Attribute(object):
  """
  An attribute.
  """
  __visibility__ = None

  def __init__(self):
    self.__name__ = None

class AbstractAttribute(_Attribute):
  """A public placeholder for abstract attributes."""
  __visibility__ = 'abstract'

  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access abstract '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access abstract '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance):
    """Raises an attribute error."""
    if instance is not None:
      raise AttributeError("Cannot access abstract '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

class PrivateAttribute(_Attribute):
  """
  A public placeholder for private attributes.

  This is the attribute that is exposed to the outside world when an
  attribute is private. If the attribute is accessed in any way, an
  AttributeError will be raised.
  """
  __visibility__ = 'private'

  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance=None):
    """Raises an attribute error."""
    if instance is not None:
      raise AttributeError("Cannot access private '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

class ProtectedAttribute(_Attribute):
  """
  A public placeholder for private attributes.

  This is the attribute that is exposed to the outside world when an
  attribute is protected. If the attribute is accessed in any way, an
  AttributeError will be raised.
  """
  __visibility__ = 'protected'

  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access protected '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access protected '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance=None):
    """Raises an attribute error."""
    if instance is not None:
      raise AttributeError("Cannot access protected '%s' object member '%s'." % (instance.__class__.__name__, self.__name__))

class _Constant(_Attribute):
  """
  An abstract constant attribute.
  """
  def __init__(self, value):
    self.__value__ = value

  def __get__(self, instance, owner=None):
    """Returns the constant value."""
    return self.__value__

  def __set__(self, instance, value):
    """Prevents the constant from being changed."""
    raise AttributeError("Cannot override '%s' object constant '%s'." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance=None):
    """Prevents the constant from being deleted."""
    if instance is not None:
      raise AttributeError("Cannot override '%s' object constant '%s'." % (instance.__class__.__name__, self.__name__))

class PublicConstant(_Constant):
  """
  A public constant object.
  """
  __visibility__ = 'public'

class ProtectedConstant(_Constant):
  """
  A protected constant object.
  """
  __visibility__ = 'protected'

class PrivateConstant(_Constant):
  """
  A private constant object.
  """
  __visibility__ = 'private'

class _Variable(_Attribute):
  """
  A abstract variable attribute.
  """
  def __init__(self, *args, **kwargs):
    try:
      args[0]
    except IndexError:
      try:
        kwargs['default']
      except KeyError:
        self.__hasdefault__ = False
        self.__default__ = None
      else:
        self.__hasdefault__ = True
        self.__default__ = kwargs['default']
    else:
      self.__hasdefault__ = True
      self.__default__ = args[0]

    for kwarg in ('type', 'validate'):
      try:
        kwargs[kwarg]
      except KeyError:
        setattr(self, '__%s__'%(kwarg,), None)
      else:
        setattr(self, '__%s__'%(kwarg,), kwargs[kwarg])
    super(_Variable, self).__init__()

  def _validate(self, value):
    """
    Validates a value.
    """
    if self.__type__ is not None:
      if not isinstance(value, self.__type__):
        try:
          if self.__type__.__interface__:
            return instanceof(value, self.__type__.__interface__)
        except AttributeError:
          pass
        if not isinstance(self.__type__, (list, tuple)):
          try:
            value = self.__type__(value)
          except TypeError:
            raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
          except ValueError:
            raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
          else:
            return value
        else:
          raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
    if self.__validate__ is not None:
      if not self.__validate__(value):
        raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
    return value

  def __get__(self, instance, owner=None):
    try:
      return instance.__dict__[self.__name__]
    except KeyError:
      if self.__hasdefault__:
        return self.__default__
      else:
        raise AttributeError("'%s' object has no attribute '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Sets the variable value."""
    instance.__dict__[self.__name__] = self._validate(value)

  def __del__(self, instance=None):
    """Deletes the variable value."""
    if instance is None:
      return
    try:
      del instance.__dict__[self.__name__]
    except KeyError:
      raise AttributeError("'%s' object has no attribute '%s'." % (instance.__class__.__name__, self.__name__))

class PublicVariable(_Variable):
  """
  A public variable attribute.
  """
  __visibility__ = 'public'

class ProtectedVariable(_Variable):
  """
  A protected variable attribute.
  """
  __visibility__ = 'protected'

class PrivateVariable(_Variable):
  """
  A private variable attribute.
  """
  __visibility__ = 'private'

class _StaticVariable(_Variable):
  """
  An abstract static variable attribute.
  """
  def __get__(self, instance, owner=None):
    """Gets the variable value."""
    try:
      return self.__value__
    except AttributeError:
      if self.__hasdefault__:
        return self.__default__
      else:
        raise AttributeError("'%s' object has no attribute '%s'." % (owner.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Sets the variable value."""
    self.__value__ = self._validate(value)

  def __del__(self, instance):
    """Deletes the variable value."""
    try:
      del self.__value__
    except KeyError:
      raise AttributeError("'%s' object has no attribute '%s'." % (instance.__class__.__class__.__name__, self.__name__))

class PublicStaticVariable(_StaticVariable):
  """
  A public static variable attribute.
  """
  __visibility__ = 'public'

class ProtectedStaticVariable(_StaticVariable):
  """
  A protected static variable attribute.
  """
  __visibility__ = 'protected'

class PrivateStaticVariable(_StaticVariable):
  """
  A private static variable attribute.
  """
  __visibility__ = 'private'

class _Method(_Attribute):
  """
  An abstract method attribute.
  """
  def __init__(self, method):
    self.__method__ = method

  def __get__(self, instance, owner=None):
    """Gets the method object."""
    def instancemethod(*args, **kwargs):
      return self.__method__(instance, *args, **kwargs)
    return instancemethod

class PublicMethod(_Method):
  """
  A public method.
  """
  __visibility__ = 'public'

class ProtectedMethod(_Method):
  """
  A protected method.
  """
  __visibility__ = 'protected'

class PrivateMethod(_Method):
  """
  A private method.
  """
  __visibility__ = 'private'

class _StaticMethod(_Method):
  """
  A abstract static method attribute.
  """
  def __get__(self, instance, owner=None):
    """Gets the method object."""
    def staticmethod(*args, **kwargs):
      return self.__method__(instance.__class__, *args, **kwargs)
    return staticmethod

class PublicStaticMethod(_StaticMethod):
  """
  A public static method.
  """
  __visibility__ = 'public'

class ProtectedStaticMethod(_StaticMethod):
  """
  A protected static method.
  """
  __visibility__ = 'protected'

class PrivateStaticMethod(_StaticMethod):
  """
  A private static method.
  """
  __visibility__ = 'private'
