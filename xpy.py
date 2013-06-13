import inspect, re

__all__ = [
  'Object',
  'const',
  'static',
  'public',
  'private',
]

class _Attribute(object):
  """
  A base extreme attribute.
  """
  def __init__(self):
    self.__name__ = None

class Constant(_Attribute):
  """
  A constant attribute.
  """
  def __init__(self, value):
    self.__value__ = value

  def __get__(self, instance, owner):
    return self.__value__

class _Method(_Attribute):
  """
  A callable attribute.
  """
  def __init__(self, callback):
    if not callable(callback):
      raise AttributeError("%s is not callable." % (callback,))
    self.__callback__ = callback

  def __get__(self, instance, owner):
    return self.__callback__

class _Member(_Attribute):
  """
  A typeable attribute.
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
    super(_Member, self).__init__()

  def _validate(self, value):
    if self.__type__ is not None:
      if not isinstance(value, self.__type__):
        raise AttributeError("Invalid attribute value %s." % (value,))
    if self.__validate__ is not None:
      if not self.__validate__(value):
        raise AttributeError("Invalid attribute value %s." % (value,))
    return value

class StaticMethod(_Method):
  """
  A static method.
  """

class StaticMember(_Member):
  """
  A static member.
  """

class PublicMethod(_Method):
  """
  A public method.
  """

class PublicMember(_Member):
  """
  A public member.
  """
  def __get__(self, instance, owner):
    """
    Gets the attribute value.
    """
    try:
      instance.__properties__
    except AttributeError:
      instance.__properties__ = {}
    try:
      return instance.__properties__[self.__name__]
    except KeyError:
      if self.__hasdefault__:
        return self.__default__
      raise AttributeError("Attribute %s not found." % (self.__name__,))

  def __set__(self, instance, value):
    """
    Sets the attribute value.
    """
    try:
      instance.__properties__
    except AttributeError:
      instance.__properties__ = {}
    instance.__properties__[self.__name__] = self._validate(value)

class StaticPublicMethod(_Method):
  """
  A static public method.
  """

class StaticPublicMember(_Member):
  """
  A static public member.
  """

class PrivateMethod(_Method):
  """
  A private method.
  """

class PrivateMember(_Member):
  """
  A private member.
  """
  def __get__(self, instance, owner):
    """
    Gets the attribute value.
    """
    i, selftext = 0, 'self.%s' % (self.__name__,)
    stacks = iter(inspect.stack())
    while i < 20:
      try:
        stack = next(stacks)
      except StopIteration:
        break
      if selftext in stack[4][0]:
        frame = stack[0]
        firstarg = frame.f_code.co_varnames[0]
        caller = frame.f_locals[firstarg]
        if caller.__class__.__name__ == instance.__class__.__name__:
          try:
            instance.__properties__
          except AttributeError:
            instance.__properties__ = {}
          try:
            return instance.__properties__[self.__name__]
          except KeyError:
            if self.__hasdefault__:
              return self.__default__
            raise AttributeError("%s object attribute %s not found." % (instance.__class__.__name__, self.__name__))
      i += 1
    raise AttributeError("%s object attribute %s not found." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """
    Sets the attribute value.
    """
    i, selftext = 0, 'self.%s' % (self.__name__,)
    stacks = iter(inspect.stack())
    while i < 20:
      try:
        stack = next(stacks)
      except StopIteration:
        break
      if selftext in stack[4][0]:
        frame = stack[0]
        firstarg = frame.f_code.co_varnames[0]
        caller = frame.f_locals[firstarg]
        if caller.__class__.__name__ == instance.__class__.__name__:
          try:
            instance.__properties__
          except AttributeError:
            instance.__properties__ = {}
          instance.__properties__[self.__name__] = self._validate(value)
          return
      i += 1
    raise AttributeError("%s attribute %s not found." % (instance.__class__.__name__, self.__name__,))

class StaticPrivateMethod(_Method):
  """
  A static private method.
  """

class StaticPrivateMember(_Member):
  """
  A static private member
  """

class _ObjectType(type):
  """
  An extreme object metaclass.
  """
  def __init__(cls, name, bases, d):
    super(_ObjectType, cls).__init__(name, bases, d)
    attributes = {}
    for key in d.keys():
      if isinstance(d[key], _Attribute):
        attributes[key] = d[key]
        attributes[key].__name__ = key
        delattr(cls, key)
    setattr(cls, '__attributes__', attributes)

class Object(object):
  """
  A base object.
  """
  __metaclass__ = _ObjectType

  def __getattribute__(self, name):
    attributes = object.__getattribute__(self, '__class__').__dict__['__attributes__']
    try:
      attribute = attributes[name]
    except KeyError:
      return object.__getattribute__(self, name)
    else:
      return attribute.__get__(self, self.__class__)

  def __setattr__(self, name, value):
    attributes = object.__getattribute__(self, '__class__').__dict__['__attributes__']
    try:
      attribute = attributes[name]
    except KeyError:
      return object.__setattr__(self, name, value)
    else:
      return attribute.__set__(self, value)

def const(value):
  if callable(value):
    raise AttributeError("Constant values may not be callable.")
  return Constant(value)

def static(*args, **kwargs):
  if len(args) == 1 and len(kwargs) == 0:
    if inspect.ismethod(args[0]):
      return StaticMethod(args[0])
    else:
      if isinstance(args[0], PublicMethod):
        return StaticPublicMethod(args[0])
      elif isinstance(args[0], PrivateMethod):
        return StaticPrivateMethod(args[0])
      elif isinstance(args[0], PublicMember):
        return StaticPublicMember(args[0])
      elif isinstance(args[0], PrivateMember):
        return StaticPrivateMember(args[0])
      else:
        return StaticMember(args[0])
  else:
    return StaticMember(*args, **kwargs)

def public(*args, **kwargs):
  if len(args) == 1 and len(kwargs) == 0:
    if inspect.ismethod(args[0]):
      return PublicMethod(args[0])
    else:
      if isinstance(args[0], StaticMethod):
        return StaticPublicMethod(args[0])
      elif isinstance(args[0], StaticMember):
        return StaticPublicMember(args[0])
      else:
        return PublicMember(args[0])
  else:
    return PublicMember(*args, **kwargs)

def private(*args, **kwargs):
  if len(args) == 1 and len(kwargs) == 0:
    if inspect.ismethod(args[0]):
      return PrivateMethod(args[0])
    else:
      if isinstance(args[0], StaticMethod):
        return StaticPrivateMethod(args[0])
      elif isinstance(args[0], StaticMember):
        return StaticPrivateMember(args[0])
      else:
        return PrivateMember(args[0])
  else:
    return PrivateMember(*args, **kwargs)
