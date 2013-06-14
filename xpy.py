# Copyright (c) 2013 Jordan Halterman
# See LICENSE for details.
from types import FunctionType, MethodType
import copy

__all__ = [
  'Object',
  'var',
  'const',
  'method',
  'public',
  'protected',
  'private',
  'static',
]

class _Attribute(object):
  """
  An attribute.
  """
  __visibility__ = None

  def __init__(self):
    self.__name__ = None

class _PrivateAttribute(_Attribute):
  """
  A public placeholder for private attributes.

  This is the attribute that is exposed to the outside world when an
  attribute is private. If the attribute is accessed in any way, an
  AttributeError will be raised.
  """
  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __det__(self, instance):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private %s object member '%s'." % (instance.__class__.__name__, self.__name__))

class _ProtectedAttribute(_Attribute):
  """
  A public placeholder for private attributes.

  This is the attribute that is exposed to the outside world when an
  attribute is protected. If the attribute is accessed in any way, an
  AttributeError will be raised.
  """
  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access protected %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access protected %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __det__(self, instance):
    """Raises an attribute error."""
    raise AttributeError("Cannot access protected %s object member '%s'." % (instance.__class__.__name__, self.__name__))

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
    raise AttributeError("Cannot override %s object constant '%s'." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance=None):
    """Prevents the constant from being deleted."""
    if instance is not None:
      raise AttributeError("Cannot override %s object constant '%s'." % (instance.__class__.__name__, self.__name__))

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
        raise AttributeError("%s object has no attribute '%s'." % (instance.__class__.__name__, self.__name__))

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
      raise AttributeError("%s object has no attribute '%s'." % (instance.__class__.__name__, self.__name__))

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
        raise AttributeError("%s object has no attribute '%s'." % (owner.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Sets the variable value."""
    self.__value__ = self._validate(value)

  def __del__(self, instance):
    """Deletes the variable value."""
    try:
      del self.__value__
    except KeyError:
      raise AttributeError("%s object has no attribute '%s'." % (instance.__class__.__class__.__name__, self.__name__))

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
    return self.__method__

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

class ObjectClass(object):
  """
  An Extreme Python object metaclass.
  """
  def __init__(self, name, bases=(), attrs=None, __doc__=None, __module__=None):
    attrs, publicattrs = attrs or {}, {}

    # Copy the full attributes dictionary into the current instance.
    self.__attrs = copy.copy(attrs)

    # Check all parent instances for inherited attributes. Note that
    # attributes may only be inherited if they're public or protected.
    for cls in bases:
      for attrname, attr in cls.__attrs.items():
        if attrname not in attrs:
          try:
            if attr.__visibility__ in ('public', 'protected'):
              attrs[attrname] = attr
          except AttributeError:
            attrs[attrname] = attr

    # Now iterate over all current class members.
    for attrname, attr in attrs.items():
      if isinstance(attr, _Attribute):
        attr.__name__ = attrname

      # Determine the attribute visibility by the __visibility__ attribute.
      try:
        visibility = attr.__visibility__
      except AttributeError:
        visibility = 'public'

      # If this is a method then wrap it. Otherwise, create an accessor.
      if isinstance(attr, _Constant):
        setattr(self, attrname, attr)
        setattr(self.__class__, attrname, attr)
      elif isinstance(attr, _StaticMethod):
        attrs[attrname] = attr.__method__
        attr = self._get_static_method_wrapper(attr.__method__)
      elif isinstance(attr, _Method):
        attrs[attrname] = attr.__method__
        attr = self._get_instance_method_wrapper(attr.__method__)
      elif isinstance(attr, FunctionType):
        attr = self._get_instance_method_wrapper(attr)
      else:
        attr = self._get_attribute_wrapper(attrname)

      # If the attribute's visibility is public, add it to the public
      # attributes. Otherwise, the private instance contains *all* attributes.
      if visibility == 'public':
        publicattrs[attrname] = attr
      else:
        if visibility == 'protected':
          publicattrs[attrname] = _ProtectedAttribute()
        else:
          publicattrs[attrname] = _PrivateAttribute()
        publicattrs[attrname].__name__ = attrname

    # If the instance does not have an __init__ method then create a
    # placeholder __init__ method.
    if not attrs.has_key('__init__'):
      attrs['__init__'] = lambda self, *args, **kwargs: None
    publicattrs['__init__'] = self._get_init_wrapper(attrs['__init__'])

    # Create an internal and external instance. The internal instance
    # contains all attributes in the object, while the external instance
    # contains only those attributes that are public.
    self.__cprivate__ = type(name, (object,), attrs)
    self.__cpublic__ = type(name, (object,), publicattrs)

  def __repr__(self):
    return self.__cprivate__.__name__

  def __call__(self, *args, **kwargs):
    return self.__cpublic__(self.__cprivate__(*args, **kwargs), *args, **kwargs)

  def _get_init_wrapper(self, init):
    """Returns an instance __init__ method wrapper."""
    def wrapped(instance, *args, **kwargs):
      private = args[0]
      instance.__private__ = private
      args = args[1:]
      init(private, *args, **kwargs)
    return wrapped

  def _get_instance_method_wrapper(self, method):
    """Returns an instance method wrapper."""
    def wrapped(instance, *args, **kwargs):
      return method(instance.__private__, *args, **kwargs)
    return wrapped

  def _get_static_method_wrapper(self, method):
    """Returns a class method wrapper."""
    return classmethod(method)

  def _get_attribute_wrapper(self, attrname):
    """Returns an attribute wrapper."""
    def getter(instance):
      return getattr(instance.__private__, attrname)
    def setter(instance, val):
      setattr(instance.__private__, attrname, val)
    def deleter(instance):
      delattr(instance.__private__, attrname)
    return property(getter, setter, deleter)

Object = ObjectClass('Object')

def var(*args, **kwargs):
  """
  Creates a publicly scoped variable attribute.
  """
  return PublicVariable(*args, **kwargs)

def const(value):
  """
  Creates a publicly scoped constant attribute.
  """
  return PublicConstant(value)

def method(meth):
  """
  Creates a publicly scoped method attribute.
  """
  return PublicMethod(meth)

def public(*args, **kwargs):
  """
  Creates a public attribute.
  """
  if len(args) == 1 and len(kwargs) == 0:
    if isinstance(args[0], FunctionType):
      return PublicMethod(args[0])
    elif isinstance(args[0], _StaticMethod):
      return PublicStaticMethod(args[0].__method__)
    elif isinstance(args[0], _Method):
      return PublicMethod(args[0].__method__)
    elif isinstance(args[0], _Constant):
      return PublicConstant(args[0].__value__)
    elif isinstance(args[0], _Variable):
      var = PublicVariable()
      for attr in ('__type__', '__validate__', '__default__', '__hasdefault__'):
        setattr(var, attr, getattr(args[0], attr))
      return var
    else:
      return PublicVariable(args[0])
  else:
    return PublicVariable(*args, **kwargs)

def protected(*args, **kwargs):
  """
  Creates a protected attribute.
  """
  if len(args) == 1 and len(kwargs) == 0:
    if isinstance(args[0], FunctionType):
      return ProtectedMethod(args[0])
    elif isinstance(args[0], _StaticMethod):
      return ProtectedStaticMethod(args[0].__method__)
    elif isinstance(args[0], _Method):
      return ProtectedMethod(args[0].__method__)
    elif isinstance(args[0], _Constant):
      return ProtectedConstant(args[0].__value__)
    elif isinstance(args[0], _Variable):
      var = ProtectedVariable()
      for attr in ('__type__', '__validate__', '__default__', '__hasdefault__'):
        setattr(var, attr, getattr(args[0], attr))
      return var
    else:
      return ProtectedVariable(args[0])
  else:
    return ProtectedVariable(*args, **kwargs)

def private(*args, **kwargs):
  """
  Creates a private attribute.
  """
  if len(args) == 1 and len(kwargs) == 0:
    if isinstance(args[0], FunctionType):
      return PrivateMethod(args[0])
    elif isinstance(args[0], _StaticMethod):
      return PrivateStaticMethod(args[0].__method__)
    elif isinstance(args[0], _Method):
      return PrivateMethod(args[0].__method__)
    elif isinstance(args[0], _Constant):
      return PrivateConstant(args[0].__value__)
    elif isinstance(args[0], _Variable):
      var = PrivateVariable()
      for attr in ('__type__', '__validate__', '__default__', '__hasdefault__'):
        setattr(var, attr, getattr(args[0], attr))
      return var
    else:
      return PrivateVariable(args[0])
  else:
    return PrivateVariable(*args, **kwargs)

def static(*args, **kwargs):
  if len(args) == 1 and len(kwargs) == 0:
    if isinstance(args[0], FunctionType):
      return PublicStaticMethod(args[0])
    elif isinstance(args[0], PublicMethod):
      return PublicStaticMethod(args[0].__method__)
    elif isinstance(args[0], ProtectedMethod):
      return ProtectedStaticMethod(args[0].__method__)
    elif isinstance(args[0], PrivateMethod):
      return PrivateStaticMethod(args[0].__method__)
    elif isinstance(args[0], PublicVariable):
      var = PublicStaticVariable()
      for attr in ('__type__', '__validate__', '__default__', '__hasdefault__'):
        setattr(var, attr, getattr(args[0], attr))
      return var
    elif isinstance(args[0], ProtectedVariable):
      var = ProtectedStaticVariable()
      for attr in ('__type__', '__validate__', '__default__', '__hasdefault__'):
        setattr(var, attr, getattr(args[0], attr))
      return var
    elif isinstance(args[0], PrivateVariable):
      var = PrivateStaticVariable()
      for attr in ('__type__', '__validate__', '__default__', '__hasdefault__'):
        setattr(var, attr, getattr(args[0], attr))
      return var
    elif isinstance(args[0], Constant):
      return args[0]
  return PublicStaticVariable(*args, **kwargs)
