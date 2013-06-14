from types import FunctionType
import copy

__all__ = [
  'Object',
  'Constant',
  'PublicVariable',
  'PrivateVariable',
  'PublicMethod',
  'PrivateMethod',
]

class _Attribute(object):
  """
  An attribute.
  """
  __visibility__ = None

  def __init__(self):
    self.__name__ = None

class PrivateAttribute(_Attribute):
  """
  A public placeholder for private attributes.
  """
  def __get__(self, instance, owner=None):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private %s object member %s." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private %s object member %s." % (instance.__class__.__name__, self.__name__))

  def __det__(self, instance):
    """Raises an attribute error."""
    raise AttributeError("Cannot access private %s object member %s." % (instance.__class__.__name__, self.__name__))

class Constant(_Attribute):
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
    raise AttributeError("Cannot override %s object constant %s." % (instance.__class__.__name__, self.__name__))

  def __del__(self, instance):
    """Prevents the constant from being deleted."""
    raise AttributeError("Cannot override %s object constant %s." % (instance.__class__.__name__, self.__name__))

class PublicConstant(Constant):
  """
  A public constant object.
  """
  __visibility__ = 'public'

class PrivateConstant(Constant):
  """
  A private constant object.
  """

class Variable(_Attribute):
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
    super(Variable, self).__init__()

  def __get__(self, instance, owner=None):
    try:
      return instance.__dict__[self.__name__]
    except KeyError:
      if self.__hasdefault__:
        return self.__default__
      else:
        raise AttributeError("%s object has not attribute %s." % (instance.__class__.__name__, self.__name__))

  def __set__(self, instance, value):
    """Sets the variable value."""
    instance.__dict__[self.__name__] = value

  def __del__(self, instance):
    """Deletes the variable value."""
    try:
      del instance.__dict__[self.__name__]
    except KeyError:
      raise AttributeError("%s object has not attribute %s." % (instance.__class__.__name__, self.__name__))

class PublicVariable(Variable):
  """
  A public variable attribute.
  """
  __visibility__ = 'public'

class PrivateVariable(Variable):
  """
  A private variable attribute.
  """
  __visibility__ = 'private'

class Method(_Attribute):
  def __init__(self, method):
    self.__method__ = method

  def __get__(self, instance, owner=None):
    return self.__method__

class PublicMethod(Method):
  __visibility__ = 'public'

class PrivateMethod(Method):
  __visibility__ = 'private'

class ObjectClass(object):
  """
  An Extreme Python object metaclass.
  """
  def __init__(self, name, bases=(), attrs=None, __doc__=None, __module__=None):
    attrs, publicattrs = attrs or {}, {}
    for attrname, attr in attrs.items():
      if isinstance(attr, _Attribute):
        attr.__name__ = attrname

      # Determine the attribute visibility by the __visibility__ attribute.
      try:
        visibility = attr.__visibility__
      except AttributeError:
        visibility = 'public'

      # If this is a method then wrap it. Otherwise, create an accessor.
      if isinstance(attr, (PublicMethod, PrivateMethod)):
        attrs[attrname] = attr.__method__
        attr = self._get_method_wrapper(attr.__method__)
      elif isinstance(attr, FunctionType):
        attr = self._get_method_wrapper(attr)
      else:
        attr = self._get_attribute_wrapper(attrname)

      # If the attribute's visibility is public, add it to the public
      # attributes. Otherwise, the private instance contains *all* attributes.
      if visibility == 'public':
        publicattrs[attrname] = attr
      else:
        publicattrs[attrname] = PrivateAttribute()
        publicattrs[attrname].__name__ = attrname

    if not attrs.has_key('__init__'):
      attrs['__init__'] = lambda self: None
    publicattrs['__init__'] = self._get_init_wrapper(attrs['__init__'])

    self.__cprivate__ = type(name, (object,), attrs)
    self.__cpublic__ = type(name, (object,), publicattrs)

  def __repr__(self):
    return self.__cprivate__.__name__

  def __call__(self, *args, **kwargs):
    return self.__cpublic__(self.__cprivate__(*args, **kwargs), *args, **kwargs)

  def _get_init_wrapper(self, init):
    def wrapped(instance, *args, **kwargs):
      private = args[0]
      instance.__private__ = private
      args = args[1:]
      init(private, *args, **kwargs)
    return wrapped

  def _get_method_wrapper(self, method):
    """Returns a method wrapper."""
    def wrapped(instance, *args, **kwargs):
      return method(instance.__private__, *args, **kwargs)
    return wrapped

  def _get_attribute_wrapper(self, attrName):
    """Returns an attribute wrapper."""
    def getter(instance):
      return getattr(instance.__private__, attrName)
    def setter(instance, val):
      setattr(instance.__private__, attrName, val)
    def deleter(instance):
      delattr(instance.__private__, attrName)
    return property(getter, setter, deleter)

Object = ObjectClass('Object')
