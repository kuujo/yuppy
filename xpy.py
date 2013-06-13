__all__ = [
  'Object',
  'const',
  'static',
  'public',
  'private',
]

class _Attribute(object):
  """
  An abstract attribute descriptor.
  """
  def __init__(self):
    self.__name__ = None

class const(_Attribute):
  """
  A constant descriptor.
  """
  def __init__(self, value):
    self.__value__ = value
    super(const, self).__init__()

  def __get__(self, instance, owner):
    return self.__value__

  def __set__(self, instance, value):
    raise AttributeError("Cannot override constant value %s." % (self.__name__,))

  def __del__(self, instance):
    raise AttributeError("Cannot override constant value %s." % (self.__name__,))

class _Var(_Attribute):
  """
  An abstract variable descriptor.
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
    super(_Var, self).__init__()

  def _validate(self, value):
    if self.__type__ is not None:
      if not isinstance(value, self.__type__):
        raise AttributeError("Invalid attribute value %s." % (value,))
    if self.__validate__ is not None:
      if not self.__validate__(value):
        raise AttributeError("Invalid attribute value %s." % (value,))
    return value

  def __set__(self, instance, value):
    """
    Implements the attribute setter interface.
    """
    instance.__dict__[self.__name__] = self._validate(value)

  def __get__(self, instance, owner):
    """
    Implements the attribute getter interface.
    """
    try:
      return instance.__dict__[self.__name__]
    except KeyError:
      if not self.__hasdefault__:
        raise AttributeError("Attribute %s not found." % (self.__name__,))
      else:
        return self.__default__

  def __del__(self, instance):
    """
    Implements the attribute deleter interface.
    """
    try:
      del instance.__dict__[self.__name__]
    except KeyError:
      raise AttributeError("Attribute %s not found." % (self.__name__,))

class public(_Var):
  """
  A public attribute.
  """

class private(_Var):
  """
  A private attribute.
  """

def static(attr):
  """
  Decorator for static attributs.
  """
  if callable(attr):
    return classmethod(attr)
  return attr

class _ObjectType(type):
  """
  An extreme object metaclass type.
  """
  def __init__(self, name, bases, d):
    type.__init__(self, name, bases, d)
    for key in d.keys():
      value = d[key]
      if isinstance(value, private):
        value.__name__ = '_%s__%s' % (name, key)
        delattr(self, key)
        setattr(self, value.__name__, value)
      elif isinstance(value, _Attribute):
        d[key].__name__ = key
        setattr(self, key, value)

class Object(object):
  """
  An extreme Python class.
  """
  __metaclass__ = _ObjectType

  def __getattr__(self, name):
    parent = super(Object, self)
    try:
      return getattr(parent, name)
    except AttributeError:
      return getattr(parent, '__%s'%(name,))
