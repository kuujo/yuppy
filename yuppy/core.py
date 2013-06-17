# Copyright (c) 2013 Jordan Halterman
# See LICENSE for details.
from types import FunctionType
import inspect, copy

from .attributes import (
  _Attribute,
  AbstractAttribute,
  ProtectedAttribute,
  PrivateAttribute,
  _Constant,
  PublicConstant,
  ProtectedConstant,
  PrivateConstant,
  _Variable,
  PublicVariable,
  ProtectedVariable,
  PrivateVariable,
  _StaticVariable,
  PublicStaticVariable,
  ProtectedStaticVariable,
  PrivateStaticVariable,
  _Method,
  PublicMethod,
  ProtectedMethod,
  PrivateMethod,
  _StaticMethod,
  PublicStaticMethod,
  ProtectedStaticMethod,
  PrivateStaticMethod,
)

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
  """
  Creates a static attribute.
  """
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
      attribute = AbstractAttribute()
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
    if cls.__name__ == 'Abstract':
      return cls
    for key, value in interface.__dict__.items():
      if isinstance(value, AbstractAttribute):
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
  try:
    if isinstance(instance, interface):
      return True
  except TypeError:
    raise TypeError("instanceof() arg 2 must be a class or type.")

  isclass = inspect.isclass(instance)
  if ducktype:
    for key, value in interface.__dict__.items():
      if isinstance(value, AbstractAttribute):
        try:
          if isclass:
            instance.__dict__[key]
          else:
            instance.__class__.__dict__[key]
        except KeyError:
          return False
    return True
  else:
    try:
      if isclass:
        return interface in instance.__interfaces__
      else:
        return interface in instance.__class__.__interfaces__
    except AttributeError:
      return False

def abstract(cls):
  """
  Creates an abstract class.
  """
  if inspect.isclass(cls):
    class Abstract(cls):
      """
      A class encapsulator.
      """
      def __init__(self, *args, **kwargs):
        if type(self) is Abstract:
          raise TypeError("Cannot instantiate abstract class '%s'." % (cls.__name__,))
        super(Abstract, self).__init__(*args, **kwargs)
    return Abstract
  else:
    attribute = AbstractAttribute()
    attribute.__name__ = cls.__name__
    return attribute

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
        attribute = PrivateAttribute()
        attribute.__name__ = key
        setattr(Object, key, attribute)
      elif value.__visibility__ == 'protected':
        attribute = ProtectedAttribute()
        attribute.__name__ = key
        setattr(Object, key, attribute)
    except AttributeError:
      continue

  return Object
