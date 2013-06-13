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

  def _get_caller(self):
    """
    Returns the calling frame.
    """
    def is_object(obj):
      def find_base(cls, bases):
        if cls in bases:
          return True
        else:
          for base in bases:
            if find_base(cls, base.__bases__):
              return True
        return False
      try:
        return find_base(Object, obj.__class__.__bases__)
      except AttributeError:
        return False

    i, selftext = 0, 'self.%s' % (self.__name__,)
    stacks = iter(inspect.stack())
    callingframe = None
    while i < 20 and callingframe is None:
      try:
        stack = next(stacks)
      except StopIteration:
        break

      # The xpy Object class uses either __getattribute__ or __setattr__ to access
      # internall class/instance attributes, so check find that call. The frame
      # immediately after __getattribute__ or __setattr__ should be the calling frame.
      code = stack[0].f_code
      if code.co_name == '__getattribute__' or code.co_name == '__setattr__' and code.co_varnames[0] == 'self':
        # If this appears to be a call from within the Object class, get the calling
        # frame and extract the calling instance (first argument).
        instance = stack[0].f_locals['self']
        if is_object(instance):
          callingframe = next(stacks)
          try:
            firstarg = callingframe[0].f_code.co_varnames[0]
          except IndexError:
            return None
          else:
            for i in range(len(callingframe[4])):
              if '%s.%s' % (firstarg, self.__name__) in callingframe[4][i]:
                return callingframe[0].f_locals[firstarg]
      i += 1
    return None

class Constant(_Attribute):
  """
  A constant attribute.
  """
  def __init__(self, value):
    self.__value__ = value

  def __get__(self, instance, owner):
    """
    Gets the attribute value.
    """
    return self.__value__

  def __set__(self, instance, value):
    """
    Raises an AttributeError to make the constant value read-only.
    """
    raise AttributeError("%s object attribute %s is read-only." % (instance.__class__.__name__, self.__name__))

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

class _Variable(_Attribute):
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
    super(_Variable, self).__init__()

  def _validate(self, value):
    """
    Validates a variable value.
    """
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

class StaticMember(_Variable):
  """
  A static member.
  """

class PublicMethod(_Method):
  """
  A public method.
  """

class PublicMember(_Variable):
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
      raise AttributeError("%s object %s not found." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """
    Sets the attribute value.
    """
    try:
      instance.__properties__
    except AttributeError:
      instance.__properties__ = {}
    instance.__properties__[self.__name__] = self._validate(value)

  def __del__(self, instance):
    """
    Deletes the attribute value.
    """
    try:
      del instance.__properties__[self.__name__]
    except AttributeError:
      pass
    except KeyError:
      raise AttributeError("%s object attribute %s not found." % (instance.__class__.__name__, self.__name__))

class StaticPublicMethod(_Method):
  """
  A static public method.
  """
  def __get__(self, instance, owner=None):
    if owner is None:
      owner = instance.__class__
    def wrap(*args, **kwargs):
      return self.__callback__(owner, *args, **kwargs)
    return wrap

class StaticPublicMember(_Variable):
  """
  A static public member.
  """
  def __get__(self, instance, owner=None):
    """
    Gets the attribute value.
    """
    if owner is None:
      owner = instance.__class__
    try:
      owner.__properties__
    except AttributeError:
      owner.__properties__ = {}
    try:
      return owner.__properties__[self.__name__]
    except KeyError:
      if self.__hasdefault__:
        return self.__default__
      raise AttributeError("%s object %s not found." % (owner.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """
    Sets the attribute value.
    """
    owner = instance.__class__
    try:
      owner.__properties__
    except AttributeError:
      owner.__properties__ = {}
    owner.__properties__[self.__name__] = self._validate(value)

  def __del__(self, instance):
    """
    Deletes the attribute value.
    """
    owner = instance.__class__
    try:
      del owner.__properties__[self.__name__]
    except AttributeError:
      pass
    except KeyError:
      raise AttributeError("%s object attribute %s not found." % (owner.__class__.__name__, self.__name__))

class PrivateMethod(_Method):
  """
  A private method.
  """
  def __get__(self, instance, owner=None):
    if owner is None:
      owner = instance.__class__
    caller = self._get_caller()
    if caller is None:
      raise AttributeError("%s object attribute %s not found." % (instance.__class__.__name__, self.__name__))
    if caller.__class__.__name__ == instance.__class__.__name:
      def wrap(*args, **kwargs):
        return self.__callback__(owner, *args, **kwargs)
      return wrap
    raise AttributeError("%s object attribute %s not found." % (instance.__class__.__name__, self.__name__))

class PrivateMember(_Variable):
  """
  A private member.
  """
  def __get__(self, instance, owner):
    """
    Gets the attribute value.
    """
    caller = self._get_caller()
    if caller is None:
      raise AttributeError("%s object attribute %s not found." % (instance.__class__.__name__, self.__name__))
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
    raise AttributeError("%s object attribute %s not found." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """
    Sets the attribute value.
    """
    caller = self._get_caller()
    if caller.__class__.__name__ == instance.__class__.__name__:
      try:
        instance.__properties__
      except AttributeError:
        instance.__properties__ = {}
      instance.__properties__[self.__name__] = self._validate(value)
    else:
      raise AttributeError("%s attribute %s not found." % (instance.__class__.__name__, self.__name__,))

class StaticPrivateMethod(_Method):
  """
  A static private method.
  """

class StaticPrivateMember(_Variable):
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
    _attributes_ = object.__getattribute__(self, '__class__').__dict__['__attributes__']
    try:
      _attribute_ = _attributes_[name]
    except KeyError:
      return object.__getattribute__(self, name)
    else:
      return _attribute_.__get__(self, self.__class__)

  def __setattr__(self, name, value):
    _attributes_ = object.__getattribute__(self, '__class__').__dict__['__attributes__']
    try:
      _attribute_ = _attributes_[name]
    except KeyError:
      return object.__setattr__(self, name, value)
    else:
      return _attribute_.__set__(self, value)

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
        return StaticPublicMethod(args[0].__callback__)
      elif isinstance(args[0], PrivateMethod):
        return StaticPrivateMethod(args[0].__callback__)
      elif isinstance(args[0], PublicMember):
        kwargs = dict(type=args[0].__type__, validate=args[0].__validate__)
        if args[0].__hasdefault__:
          kwargs['default'] = args[0].__default__
        return StaticPublicMember(**kwargs)
      elif isinstance(args[0], PrivateMember):
        kwargs = dict(type=args[0].__type__, validate=args[0].__validate__)
        if args[0].__hasdefault__:
          kwargs['default'] = args[0].__default__
        return StaticPrivateMember(**kwargs)
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
        return StaticPublicMethod(args[0].__callback__)
      elif isinstance(args[0], StaticMember):
        kwargs = dict(type=args[0].__type__, validate=args[0].__validate__)
        if args[0].__hasdefault__:
          kwargs['default'] = args[0].__default__
        return StaticPublicMember(**kwargs)
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
        return StaticPrivateMethod(args[0].__callback__)
      elif isinstance(args[0], StaticMember):
        kwargs = dict(type=args[0].__type__, validate=args[0].__validate__)
        if args[0].__hasdefault__:
          kwargs['default'] = args[0].__default__
        return StaticPrivateMember(**kwargs)
      else:
        return PrivateMember(args[0])
  else:
    return PrivateMember(*args, **kwargs)
