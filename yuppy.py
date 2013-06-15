# Copyright (c) 2013 Jordan Halterman
# See LICENSE for details.
from types import FunctionType
import inspect, copy

__all__ = [
  'encapsulate',
  'variable',
  'var',
  'constant',
  'const',
  'method',
  'public',
  'protected',
  'private',
  'static',
  'final',
  'abstract',
  'interface',
  'implements',
  'instanceof',
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
  __visibility__ = 'private'

  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance=None):
    """Raises an attribute error."""
    if instance is not None:
      raise AttributeError("Cannot access private %s object member '%s'." % (instance.__class__.__name__, self.__name__))

class _ProtectedAttribute(_Attribute):
  """
  A public placeholder for private attributes.

  This is the attribute that is exposed to the outside world when an
  attribute is protected. If the attribute is accessed in any way, an
  AttributeError will be raised.
  """
  __visibility__ = 'protected'

  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access protected %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access protected %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance=None):
    """Raises an attribute error."""
    if instance is not None:
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

def variable(*args, **kwargs):
  """
  Creates a publicly scoped variable attribute.
  """
  return PublicVariable(*args, **kwargs)

def var(*args, **kwargs):
  """
  Alias for the variable decorator.
  """
  return variable(*args, **kwargs)

def constant(value):
  """
  Creates a publicly scoped constant attribute.
  """
  return PublicConstant(value)

def const(*args, **kwargs):
  """
  Alias for the constant decorator.
  """
  return constant(*args, **kwargs)

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

def final(cls):
  """
  Prevents a class definition from being extended.
  """
  if not inspect.isclass(cls):
    raise TypeError("The 'final' decorator only supports classes.")

  cls = encapsulate(cls)
  def constructor(*args, **kwargs):
    return cls(*args, **kwargs)
  constructor.__name__ = cls.__name__
  return constructor

def interface(cls):
  """
  Creates an interface.
  """
  for key, value in cls.__dict__.items():
    if not (key.startswith('__') and key.endswith('__')):
      attribute = _AbstractAttribute()
      attribute.__name__ = key
      setattr(cls, key, attribute)

  def classnew(cls, *args, **kwargs):
    raise TypeError("Cannot instantiate interface '%s'." % (cls.__name__,))
  cls.__new__ = classmethod(classnew)
  cls.__interface__ = True
  return cls

def implements(interface):
  """
  Implements an interface.
  """
  def wrap(cls):
    for key, value in interface.__dict__.items():
      if isinstance(value, _AbstractAttribute):
        try:
          cls.__dict__[key]
        except KeyError:
          raise TypeError("'%s' definition missing attribute '%s' from '%s' interface." % (cls.__name__, key, interface.__name__))
    try:
      cls.__interfaces__
    except AttributeError:
      cls.__interfaces__ = set()
    cls.__interfaces__.add(interface)
    return cls
  return wrap

def instanceof(instance, interface, ducktype=True):
  """
  Type checks an instance for an interface.
  """
  if isinstance(instance, interface):
    return True
  if ducktype:
    for key, value in interface.__dict__.items():
      if isinstance(value, _AbstractAttribute):
        try:
          instance.__class__.__dict__[key]
        except KeyError:
          return False
    return True
  else:
    try:
      return interface in instance.__class__.__interfaces__
    except AttributeError:
      return False

def abstract(cls):
  """
  Creates an abstract class.
  """
  class Abstract(cls):
    """
    A class encapsulator.
    """
    def __init__(self, *args, **kwargs):
      if type(self) is AbstractClass:
        raise TypeError("Cannot instantiate abstract class '%s'." % (cls.__name__,))
      self.__dict__['__private__'] = cls(*args, **kwargs)

    def __getattr__(self, name):
      return getattr(self.__private__, name)

    def __setattr__(self, name, value):
      return setattr(self.__private__, name, value)

    def __delattr__(self, name):
      return delattr(self.__private__, name)

  return Abstract

def encapsulate(cls):
  """
  Encapsulates a class.
  """
  if not inspect.isclass(cls):
    raise TypeError("Only classes may be encapsulated.")

  # If any parents of this class have already been decorated, dynamically
  # remove the decoration.
  cls = copy.copy(cls)
  current = cls
  while True:
    try:
      if current.__bases__[0].__name__ == 'Object':
        current.__bases__ = current.__bases__[0].__bases__
    except IndexError:
      break
    else:
      current = current.__bases__[0]

  # Apply variable names to definitions.
  def apply_names(attrs):
    for key, value in attrs.items():
      if isinstance(value, _Attribute):
        value.__name__ = key

  apply_names(cls.__dict__)

  def get_definition(self, name):
    def find_definition(cls):
      for base in cls.__bases__:
        try:
          return base.__dict__[name]
        except KeyError:
          return find_definition(base)
        except AttributeError:
          return None
      return None

    try:
      return self.__dict__[name]
    except KeyError:
      try:
        return cls.__dict__[name]
      except KeyError:
        definition = find_definition(cls)
        if definition is None:
          raise AttributeError("'%s' object has no attribute '%s'." % (cls, name))
        else:
          return definition

  def get_visibility(self, name):
    definition = get_definition(self, name)
    try:
      return definition.__visibility__
    except AttributeError:
      return 'public'

  def is_child(self, _cls):
    def find_root(_cls):
      for base in _cls.__bases__:
        if base is Object:
          return find_root(base)
      return _cls
    return cls in find_root(_cls).__bases__

  def call(self, callback, attr, *args):
    visibility = get_visibility(self, attr)
    if visibility == 'public':
      return callback(self.__private__, attr, *args)
    elif visibility == 'protected':
      if self.__class__ is not Object and is_child(self, self.__class__):
        return callback(self.__private__, attr, *args)
      else:
        raise AttributeError("Cannot access %s '%s' member '%s'." % (visibility, cls.__name__, attr))
    else:
      raise AttributeError("Cannot access %s '%s' member '%s'." % (visibility, cls.__name__, attr))

  class Object(cls):
    """
    A class encapsulator.
    """
    def __init__(self, *args, **kwargs):
      self.__dict__['__private__'] = cls(*args, **kwargs)
      super(Object, self).__init__(*args, **kwargs)

    def __getattribute__(self, name):
      """
      Supports accessing all attributes.

      If an attribute begins and ends with two underscores, it is not processed for
      accessibility. All other members are checked for accessibility.
      """
      if name.startswith('__') and name.endswith('__'):
        return cls.__getattribute__(self, name)
      return call(self, cls.__getattribute__, name)

    def __setattr__(self, name, value):
      return call(self, setattr, name, value)

    def __delattr__(self, name):
      return call(self, delattr, name)

    def __repr__(self):
      return repr(self.__private__)

    def __str__(self):
      return str(self.__private__)

  # Apply private or protected attributes to the decorator.
  for key, value in cls.__dict__.items():
    try:
      if value.__visibility__ == 'private':
        attribute = _PrivateAttribute()
        attribute.__name__ = key
        setattr(Object, key, attribute)
      elif value.__visibility__ == 'protected':
        attribute = _ProtectedAttribute()
        attribute.__name__ = key
        setattr(Object, key, attribute)
    except AttributeError:
      continue

  return Object

class _AbstractAttribute(_Attribute):
  """An abstract attribute."""
  __visibility__ = 'abstract'

  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access abstract %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access abstract %s object member '%s'." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance):
    """Raises an attribute error."""
    if instance is not None:
      raise AttributeError("Cannot access abstract %s object member '%s'." % (instance.__class__.__name__, self.__name__))
