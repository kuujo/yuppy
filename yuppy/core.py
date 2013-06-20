# Copyright (c) 2013 Jordan Halterman
# See LICENSE for details.
from types import FunctionType, MethodType
import inspect

class Attribute(object):
  """
  A basic attribute.
  """
  __name__ = None

def isattribute(obj):
  """
  Returns a boolean value indicating whether an object is an attribute.
  """
  return isinstance(obj, Attribute)

def constant(value):
  """
  Decorator for creating a constant class/instance variable.
  """
  return Constant(value)

const = constant

class Constant(Attribute):
  """
  A constant attribute.
  """
  def __init__(self, value):
    self.__value__ = value

  def __get__(self, instance=None, owner=None):
    """Returns the constant value."""
    return self.__value__

  def __set__(self, instance, value):
    """Raises an attribute error when an attempt is made to override the constant value."""
    raise AttributeError("Cannot override constant value.")

  def __del__(self, instance):
    """Raises an attribute error when an attempt is made to delete the constant value."""
    raise AttributeError("Cannot delete constant value.")

def isconstant(obj):
  """
  Indicates whether an object is a constant value.
  """
  return isinstance(obj, Constant)

isconst = isconstant

def variable(*args, **kwargs):
  """
  Decorator for creating an instance variable.
  """
  return Variable(*args, **kwargs)

var = variable

class Variable(Attribute):
  """
  A variable attribute.
  """
  def __init__(self, *args, **kwargs):
    if len(args) == 0:
      self.__type__ = None
    elif len(args) == 1:
      if not isinstance(args[0], (list, tuple)):
        self.__type__ = (args[0],)
      else:
        self.__type__ = args[0]
    else:
      self.__type__ = args
    try:
      kwargs['default']
    except KeyError:
      self.__hasdefault__ = False
      self.__default__ = None
    else:
      self.__hasdefault__ = True
      self.__default__ = kwargs['default']
    try:
      self.__validate__ = kwargs['validate']
    except KeyError:
      self.__validate__ = None
    try:
      self.__interface__ = kwargs['interface']
    except KeyError:
      self.__interface__ = None
    super(Variable, self).__init__()

  def _validate(self, value):
    """
    Validates a value.
    """
    if self.__interface__ is not None and not instanceof(value, self.__interface__):
      raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
    if self.__type__ is not None and not isinstance(value, self.__type__):
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

  def __get__(self, instance=None, owner=None):
    """Gets the variable value."""
    try:
      return instance.__dict__[self.__name__]
    except KeyError:
      if self.__hasdefault__:
        return self.__default__
      else:
        raise AttributeError("'%s' object has no attribute '%s'." % (instance.__class__.__name__, self.__name__))
    except AttributeError:
      raise AttributeError("Instance member '%s' cannot be accessed from the class scope." % (self.__name__,))

  def __set__(self, instance, value):
    """Sets the variable value."""
    try:
      instance.__dict__
    except AttributeError:
      raise AttributeError("Instance member '%s' cannot be accessed from the class scope." % (self.__name__,))
    else:
      instance.__dict__[self.__name__] = self._validate(value)

  def __del__(self, instance=None):
    """Sets the variable value to None."""
    if instance is not None:
      try:
        instance.__dict__[self.__name__] = None
      except AttributeError:
        raise AttributeError("Instance member '%s' cannot be accessed from the class scope." % (self.__name__,))

  def default(self, value):
    """
    Sets the variable default value.
    """
    self.__default__ = value
    return self

  def validate(self, validator):
    """
    Sets the variable validator.
    """
    if isinterface(validator):
      self.__interface__ = validator
    else:
      self.__validate__ = validator
    return self

def isvariable(obj):
  """
  Indicates whether an object is a variable.
  """
  return isinstance(obj, Variable)

isvar = isvariable

def static(*args, **kwargs):
  """
  Decorator for creating a static (class) variable.
  """
  return StaticVariable(*args, **kwargs)

stat = static

class StaticVariable(Variable):
  """
  A static variable attribute.
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

def isstatic(obj):
  """
  Indicates whether an object is a static variable.
  """
  return isinstance(obj, StaticVariable)

isstat = isstatic

def method(meth):
  """
  Decorator for creating a method.
  """
  return Method(meth)

class Method(Attribute):
  """
  A method attribute.
  """
  def __init__(self, method):
    self.__method__ = method
    self.__params__ = None

  def __get__(self, instance=None, owner=None):
    """Gets the method, applying type hinting to method arguments."""
    if self.__params__ is None:
      return MethodType(self.__method__, instance)
    posargs, varargs, keywords, defaults = inspect.getargspec(self.__method__)
    posargs = posargs[1:]
    def wrap(inst, *args, **kwargs):
      for i in range(len(posargs)):
        try:
          self.__params__[posargs[i]]
        except KeyError:
          continue
        # Try to find the parameter in positional arguments.
        try:
          self.__validate_argument(posargs[i], args[i], self.__params__[posargs[i]])
        except IndexError:
          # Try to find the parameter in keyword arguments.
          try:
            self.__validate_argument(posargs[i], kwargs[posargs[i]], self.__params__[posargs[i]])
          except KeyError:
            pass
      return self.__method__(inst, *args, **kwargs)
    return MethodType(wrap, instance)

  def __validate_argument(self, name, value, type):
    """
    Validates an argument value.
    """
    if isinterface(type) and not instanceof(value, type):
      raise TypeError("Method argument '%s' must be an implementation of '%s'." % (name, type.__name__))
    elif not isinstance(value, type):
      raise TypeError("Method argument '%s' must be an instance of '%s'." % (name, type))
    if not instanceof(value, type):
      raise TypeError("Method argument '%s' must implement the same interface as %s." % (name, type))

def params(**kwargs):
  """
  Decorator for defining parameter types.
  """
  def wrap(meth):
    if not isinstance(meth, Method):
      meth = Method(meth)
    args = inspect.getargspec(meth.__method__)[0]
    for key in kwargs:
      if key not in args:
        raise ValueError("Invalid parameter key '%s'. That parameter was not found." % (key,))
    meth.__params__ = kwargs
    return meth
  return wrap

def abstract(obj):
  """
  Makes a class or method abstract.
  """
  if inspect.isclass(obj):
    obj.__abstract__ = True
    return obj
  else:
    if isinstance(obj, FunctionType):
      return AbstractMethod(obj)
    raise TypeError("Invalid abstract attribute %s." % (obj,))

class AbstractMethod(Method):
  """
  An abstract method attribute.
  """
  def __init__(self, method):
    self.__abstract__ = True
    super(AbstractMethod, self).__init__(method)

  def __get__(self, instance=None, owner=None):
    raise AttributeError("Cannot call abstract method %s." % (self.__method__.__name__,))

def isabstract(obj):
  """
  Returns a boolean value indicating whether an object is abstract.
  """
  if hasattr(obj, '__dict__'):
    return obj.__dict__.get('__abstract__', False)
  else:
    return getattr(obj, '__abstract__', False)

def final(obj):
  """
  Makes a class or method final.
  """
  if inspect.isclass(obj):
    obj.__final__ = True
    return obj
  else:
    if isinstance(obj, FunctionType):
      return FinalMethod(obj)
    raise TypeError("Invalid final attribute %s." % (obj,))

class FinalMethod(Method):
  """
  A final method attribute.
  """
  def __init__(self, method):
    self.__final__ = True
    super(FinalMethod, self).__init__(method)

def isfinal(obj):
  """
  Returns a boolean value indicating whether an object is final.
  """
  return getattr(obj, '__final__', False)

class StaticType(type):
  """
  A base yuppy static type.
  """
  def _findattr(cls, attrname, *args):
    for base in cls.__mro__:
      try:
        return base.__dict__[attrname]
      except KeyError:
        continue

    if len(args) > 0:
      return args[0]
    else:
      raise AttributeError("Attribute not found.")

  @property
  def __attributes__(cls):
    attrs = {}
    for base in cls.__mro__:
      for attrname, attr in base.__dict__.items():
        if attrname not in attrs and isattribute(attr):
          attrs[attrname] = attr
    return attrs

  def __getattr__(cls, name):
    """Supports accessing attributes via class calls."""
    attr = cls._findattr(name, None)
    if isattribute(attr):
      return getattr(cls, name)
    return super(StaticType, cls).__getattr__(name, value)

  def __setattr__(cls, name, value):
    """Prevents overriding explicitly set attributes."""
    if isinstance(name, basestring) and not (name.startswith('__') and name.endswith('__')):
      if isattribute(cls._findattr(name, None)):
        raise AttributeError("Cannot override '%s' attribute '%s' by assignment." % (cls.__name__, name))
    super(StaticType, cls).__setattr__(name, value)

  def __delattr__(cls, name):
    """Prevents deleting explicitly set attributes."""
    if isinstance(name, basestring) and not (name.startswith('__') and name.endswith('__')):
      if isattribute(cls._findattr(name, None)):
        raise AttributeError("Cannot delete '%s' attribute '%s'." % (cls.__name__, name))
    super(StaticType, cls).__delattr__(name)

class ObjectType(StaticType):
  """
  A yuppy class type.
  """
  def __init__(cls, name, bases, attrs):
    super(ObjectType, cls).__init__(name, bases, attrs)
    class_isabstract = False
    interfaces = getattr(cls, '__interfaces__', [])
    for interface in interfaces:
      for base in interface.__mro__:
        for attrname, attr in base.__dict__.items():
          if isinstance(getattr(base, attrname), (FunctionType, MethodType)):
            if not hasattr(cls, attrname):
              raise TypeError("'%s' contains an abstract method '%s' and must be declared abstract." % (name, attrname))
            elif not isinstance(getattr(cls, attrname), (FunctionType, MethodType)):
              raise TypeError("'%s' attribute '%s' is not a method." % (name, attrname))

    for base in cls.__mro__:
      if isfinal(base) and cls is not base:
        raise TypeError("Cannot override final class '%s'." % (base.__name__,))
      for attrname, attr in base.__dict__.items():
        if isattribute(attr):
          attr.__name__ = attrname
        if isabstract(attr):
          func = cls._findattr(attrname)
          try:
            func = func.__method__
          except AttributeError:
            pass
          try:
            meth = attr.__method__
          except AttributeError:
            meth = attr
          if func is meth:
            class_isabstract = True
        if base is not cls and isfinal(attr):
          func = cls._findattr(attrname)
          try:
            func = func.__method__
          except AttributeError:
            pass
          try:
            func = func.im_func
          except AttributeError:
            pass
          try:
            meth = attr.__method__
          except AttributeError:
            meth = attr
          if func is not meth:
            raise TypeError("Cannot override final '%s' method '%s'." % (base.__name__, attrname))

    if class_isabstract:
      setattr(cls, '__abstract__', True)

class Object(object):
  """
  A yuppy base class.
  """
  __metaclass__ = ObjectType
  def __new__(cls, *args, **kwargs):
    if isabstract(cls):
      raise TypeError("Cannot instantiate abstract class '%s'." % (cls.__name__,))
    return object.__new__(cls, *args, **kwargs)

  def __setattr__(self, name, value):
    if isattribute(value):
      setattr(self.__class__, name, value)
    else:
      super(Object, self).__setattr__(name, value)

def yuppy(cls):
  """
  Decorator for yuppy classes.
  """
  class Object(cls):
    __metaclass__ = ObjectType
    def __new__(cls, *args, **kwargs):
      if isabstract(cls):
        raise TypeError("Cannot instantiate abstract class '%s'." % (cls.__name__,))
      return object.__new__(cls, *args, **kwargs)
    def __setattr__(self, name, value):
      if isattribute(value):
        setattr(self.__class__, name, value)
      else:
        super(Object, self).__setattr__(name, value)
  Object.__name__ = cls.__name__
  return Object

def isyuppyclass(cls):
  """
  Indicates whether a class is a Yuppy class.
  """
  try:
    return cls.__metaclass__ is ClassType
  except AttributeError:
    return False

isyuppy = isyuppyclass

class InterfaceType(StaticType):
  """
  A yuppy interface.
  """
  def __init__(cls, name, bases, attrs):
    for attrname, attr in attrs.items():
      if isattribute(attr):
        attr.__name__ = attrname
      if not attrname.startswith('_') and isinstance(attr, FunctionType):
        attrs[attrname] = AbstractMethod(attr)
    super(InterfaceType, cls).__init__(name, bases, attrs)

class Interface(object):
  """
  A yuppy interface class.
  """
  __metaclass__ = InterfaceType

  def __new__(cls, *args, **kwargs):
    """Raises a TypeError when the interface is instantiated."""
    raise TypeError("Cannot instantiate interface '%s'." % (cls.__name__,))

def isinterface(cls):
  """
  Indicates whether the given class is an interface.
  """
  return isinstance(cls, Interface)

def instanceof(obj, interface, ducktype=True):
  """
  Indicates whether the given object is an instance of the given interface.
  """
  if ducktype:
    for base in interface.__mro__:
      for attrname, attr in base.__dict__.items():
        if isinstance(getattr(base, attrname), FunctionType):
          if not hasattr(obj, attrname):
            return False
          elif not isinstance(getattr(obj, attrname), FunctionType):
            return False
    return True
  else:
    if isinstance(obj, interface):
      return True
    try:
      if interface in obj.__interfaces__:
        return True
      else:
        return False
    except AttributeError:
      return False

def implements(interface):
  """
  Decorator for implementing an interface.

  Wraps the implementing class in an Object if necessary, and adds the implementation.
  The class is then extended so as to invoke the ObjectType.__init__() method in order
  to check for adherence to the given interface.
  """
  def wrap(cls):
    if not isyuppyclass(cls):
      cls = yuppy(cls)
    try:
      cls.__interfaces__
    except AttributeError:
      cls.__interfaces__ = []
    if interface not in cls.__interfaces__:
      cls.__interfaces__.append(interface)
    class _Implements(cls):
      pass
    _Implements.__name__ = cls.__name__
    return _Implements
  return wrap
