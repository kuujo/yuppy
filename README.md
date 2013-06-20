## Yuppy
#### Python Programming for the Privileged Class
-----

_Yuppy is released under the [MIT License](http://opensource.org/licenses/MIT)._

Yuppy is a small Python library that integrates seamlessly with your
application to promote data integrity by supporting common object-oriented
language features. It intends to provide fully integrated support for
interfaces, abstract classes and methods, final classes and methods, and
type hinting in a manner that preserves much of the dynamic nature of Python.
Yuppy can improve the integrity of your data and the stability of your code
without comprimising usability. It is easy to use and is intentionally
designed to fit with the Python development culture, not circumvent it.

### Table of contents
-------------------
1. [Introduction](#but-type-checking-is-bad)
1. [Class Decorators](#class-decorators)
   * [The Yuppy Decorator](#yuppy-1)
   * [Abstract Classes](#abstract)
   * [Final Classes](#final)
1. [Member Decorators](#member-decorators)
   * [Constants](#constant)
   * [Variables](#variable)
   * [Static Variables](#static)
   * [Methods](#method)
   * [Abstract Methods](#abstract-1)
   * [Final Methods](#final-1)
   * [Type Validation](#type-validation)
1. [Interfaces](#interfaces)
   * [Interfaces](#interface)
   * [Implements](#implements)
   * [Type Checking](#instanceof)
1. [Type Hinting](#type-hinting)
   * [Typed Parameters](#params)

##### _"But type checking is bad!"_
Yuppy does type checking in a manner that is in keeping with the dynamic
nature of Python. Yuppy [interface checks](#instanceof) can be based on
duck-typing, so any class can serve as a Yuppy interface. This feature
simply serves as a more efficient way to determine whether any given
object walks and talks like a duck.


## Class Decorators

### yuppy
Declares a Yuppy class definition.

```
yuppy(cls)
```

This decorator is not required to implement a Yuppy class. The recommended
alternative to using the `yuppy` decorator is to use the `yuppy.Object`
superclass in your class definition. The decorator simply dynamically
extends any class to include the `yuppy.Object` class in its hierarchy.

```python
from yuppy import Object, yuppy

class Apple(Object):
  """This is a Yuppy class."""

@yuppy
class Apple(Object):
  """This is also a Yuppy class."""
```

### abstract
Creates an abstract class.

```
abstract(cls)
```

Abstract classes are classes that cannot themselves be instantiates, but
can be extended and instantiated.

##### Example
```python
from yuppy import Object, abstract

@abstract
class Apple(Object):
  """An abstract apple."""
  weight = protected(float)

  def get_weight(self):
    return self.weight

  def set_weight(self, weight):
    self.weight = weight

class GreenApple(Apple):
  """A concrete green apple."""
```

We will be able to create instances of `GreenApple`, which inherits from
`Apple`, but any attempts to instantiate an `Apple` will result in a
`TypeError`.

```
>>> apple = GreenApple()
>>> apple.set_weight(1.0)
>>> apple.get_weight()
1.0
>>> apple = Apple()
TypeError: Cannot instantiate abstract class 'Apple'.
```

### final
Declares a class definition to be final.

The final Yuppy decorator is, well, `final`, which allows users to define
classes that _cannot be extended._ This is a common feature in several
other object-oriented languages.
```
final(cls)
```

##### Example

```python
from yuppy import Object

@final
class Apple(Object):
  weight = var(float, default=None)
```

```
>>> apple = Apple()
>>> class GreenApple(Apple):
...   pass
...
TypeError: ...
```

## Member Decorators

### variable
Creates a variable attribute.
```
variable([default=None[, validate=None[, *types]]])
var([default=None[, validate=None[, *types]]])
```

##### Example
```python
from yuppy import Object

class Apple(Object):
  foo = var(int, default=None, validate=lambda x: x == 1)
```

```
>>> apple = Apple()
```

### static
Creates a static attribute.

Static Yuppy members are equivalent to standard Python class members. This is
essentially the same parallel that exists between Python's class members
and static variables in many other object-oriented languages. With Yuppy we
can use the `static` decorator to create static methods or properties.

```
static([default=None[, validate=None[, *types]]])
```

##### Example

```python
from yuppy import Object, static

class Apple(Object):
  """An abstract apple."""
  weight = static(float, default=None)
```

With static members, changes to a member variable will be applied to
all instances of the class. So, even after instantiating a new instance
of the class, the `weight` attribute value will remain the same.

```
>>> apple1 = Apple()
>>> apple1.weight
None
>>> apple1.weight = 2.0
>>> apple1.weight
2.0
>>> apple2 = Apple()
>>> apple2.weight
2.0
```

### constant
Creates a constant attribute.

Constants are attributes which have a permanent value. They can be used for
any value which should never change within the application, such as an
application port number, for instance. With Yuppy we can use the `const`
decorator to create a constant, passing a single permanent value to the
constructor.
```
constant(value)
const(value)
```

##### Example
```python
from yuppy import Object, const

class RedApple(Object):
  color = const('red')
```

Note that while the class constant can be overridden, the instance constant
will not change regardless of the class constant value.

```
>>> RedApple.color
'red'
>>> apple = RedApple()
>>> apple.color
'red'
>>> RedApple.color = 'blue'
AttributeError: Cannot override 'RedApple' attribute 'color' by assignment.
>>> RedApple.color
'red'
>>> apple.color
'red'
>>> apple = RedApple()
>>> apple.color
'red'
>>> apple.color = 'blue'
AttributeError: Cannot override 'Apple' attribute 'color' by assignment.
```

### method
Creates a method attribute.
```
method(callback)
```

##### Example
```python
from yuppy import Object, var, method

class Apple(Object):
  color = var(default='red')

  @method
  def getcolor(self):
    return self.color
```

```
>>> apple = Apple()
>>> apple.getcolor()
'red'
```

### abstract
Creates an abstract method.
```
abstract(method)
```

Abstract methods can be applied to *any* python class, even without
declaring the class to be abstract. This means that if the method is
not re-defined in a child class, an `AttributeError` will be raised if
the abstract method is accessed. Therefore, it is strongly recommended
that any class that contains abstract methods be declared abstract.

##### Example
```python
from yuppy import abstract, Object

@abstract
class Apple(Object):
  """An abstract apple."""
  @abstract
  def get_color(self):
    """Gets the apple color."""
```

Once we've defined an abstract class, we can extend it and override the
abstract methods.

```
>>> class GreenApple(Object):
...   def get_color(self):
...     return 'green'
...
>>> apple = GreenApple()
>>> apple.get_color()
'green'
```

Note what happens if we try to use abstract methods or fail to override them.

```
>>> class GreenApple(Object):
...   pass
...
>>> # We can still instantiate green apples since the class isn't declared abstract.
>>> apple = GreenApple()
>>> # But we can't access the get_color() method.
>>> apple.get_color()
AttributeError: Cannot access abstract 'GreenApple' object member 'bar'.
```

### final
Creates a final method.
```
final(method)
```

Similar to final classes, final methods cannot be overridden. When a class
attempts to override a final method, a `TypeError` will be raised.

##### Example

```python
from yuppy import Object, final

class RedApple(Object):
  @final
  def getcolor(self):
    return 'red'
```

```
>>> class BlueApple(RedApple):
...   def getcolor(self):
...     return 'blue'
...
TypeError: Cannot override final 'RedApple' method 'getcolor'.
```

### Type Validation
Yuppy can perform direct type checking and arbitrary execution of validation
callbacks. When a mutable Yuppy attribute is set, validators will automatically
be executed. This ensures that values are validated at the time they're
set rather than when they're accessed.

Any `var` type can perform data validation. When creating a new `var`,
we can pass either `<type>` or `validate=<func>` to the object
constructor.

##### Example

```python
from yuppy import Object, var

class Apple(Object):
  """An abstract apple."""
  weight = var(float)

  def __init__(self, weight):
    self.weight = weight
```

Now, if we create an `Apple` instance we can see how the validation works.
Note that if an improper value is passed to the constructor, the validator
will automatically try to cast it to the correct type if only one type
is provided.

```
>>> apple = Apple(1)
>>> apple = Apple('one')
AttributeError: Invalid attribute value for 'weight'.
```

Note also that instance variable type checking is integrated with the
Yuppy interface system. This means that an interface can be passed to
any variable definition as the `type` argument, and Yuppy will validate
variable values based on duck typing. This can be very useful within the
context of the Python programming language.

## Interfaces
Interfaces are a partcilarly useful feature with Python. Since Python
promotes duck typing, Yuppy interfaces can be used to ensure that any
object walks and talks like a duck. For this reason, Yuppy interface
evaluation supports both explicit interface implementation checks _and_
implicit interface implementation checks, or duck typing.

### Interface
An abstract base class for interfaces.

The `yuppy.Interface` class is the equivalent of `yuppy.Object` for interfaces.
Abstract interface attributes are declared by simply creating them. Yuppy
will evaluate the interface for any public attributes and consider those
to be required of any implementing classes.

##### Example

```python
from yuppy import Interface

class AppleInterface(Interface):
  """An apple interface."""
  def get_color(self):
    """Returns the apple color."""

  def get_weight(self):
    """Returns the apple weight."""
```

Note that the `yuppy.Interface` class is _not required to create an interface._
Yuppy can do interface checking based on duck-typing. Simply defining _any_
class and passing it to the `yuppy.instanceof` method will results in a simple
comparison of each object's attributes.

For example:

```python
class IFoo(object):
  def foo(self):
    pass
  def bar(self):
    pass
```

An instance of _any_ class that contains the methods `foo` and `bar` will
be considered an instance of the `IFoo` interface.

```
>>> from yuppy import instanceof
>>> class Foo(object):
...   def foo(self):
...     pass
...   def bar(self):
...     pass
...
>>> foo = Foo()
>>> instanceof(foo, IFoo)
True
```

### implements
Declares a class definition to implement an interface.

When a class implements an interface, it must define all abstract attributes
of that interface. Yuppy will automatically evaluate the class definition
to ensure it conforms to the indicated interface.

##### Example
Continuing with the previous example, we can implement the `AppleInterface`
interface.

```
>>> from yuppy import Object, implements
>>> @implements(AppleInterface)
... class Apple(Object):
...   """An apple."""
...
TypeError: 'Apple' contains an abstract method 'get_color' and must be declared abstract.
```

Note that if we don't implement the `AppleInterface` attributes a `TypeError`
will be raised. Let's try that again.

```
>>> from yuppy import implements, Object, const
>>> @implements(AppleInterface)
... class Apple(Object):
...   """An apple."""
...   color = const('red')
...   weight = const(2.0)
...   def get_color(self):
...     """Returns the apple color."""
...     return self.color
...   def get_weight(self):
...     """Returns the apple weight."""
...     return self.weight
...
>>> apple = Apple()
>>> apple.get_color()
'red'
```

### instanceof
Determines whether an instance's class implements an interface.

```
implements(instance, interface[, ducktype=True])
```

Finally, it's important that we be able to evaluate objects for adherence
to any interface requirements. The `instanceof` function behaves similarly
to Python's built-in `isinstance` function, but for Yuppy interfaces.
However, _Yuppy's implementation can also evaluate interface implementation
based on duck typing._ This means that object classes do not necessarily
have to implement a specific interface, they simply need to behave in the
manner that the interface requires.

```
>>> from yuppy import instanceof
>>> apple = Apple()
>>> instanceof(apple, AppleInterface)
True
>>> instanceof(apple, AppleInterface, False)
True
>>> instanceof(apple, Apple)
True
```

## Type Hinting
With Yuppy providing all these type checking features, that would normally
mean a lot more calls to the Yuppy API to validate data. But luckily Yuppy
provides an API for that, as well. Yuppy uses decorators to perform type
hinting for method parameters.

### params
Defines method parameter types.

The `params` decorator can set required parameter types using _any_ python
class or Yuppy interface. This allows for flexible type checking based on
either `isinstance` or straight duck-typing.

```python
from yuppy import Object, params

class Apple(Object):
  """A base apple."""
  color = var(basestring, default='red')

  @params(color=basestring)
  def set_color(self, color='red'):
    self.color = color

  @params(weight=(float, int))
  def set_weight(self, weight):
    self.weight = weight
```

If we pass invalid values to type hinted methods, a `TypeError` will be raised.

```
>>> apple = Apple()
>>> apple.set_color('blue')
>>> apple.set_color(1)
TypeError: Method argument 'color' must be an instance of '<type 'basestring'>'.
>>> # Note that it still handles default arguments, as well.
>>> apple.set_color()
>>> apple.set_weight('two')
TypeError: Method argument 'weight' must be an instance of '(<type 'float'>, <type 'int'>)'.
```

Also, remember that Yuppy type checking can be interface-based.

```python
from yuppy import Object, params

class IApple(object):
  def get_color(self):
    pass
  def get_weight(self):
    pass

class AppleTree(Object):
  def __init__(self):
    self.apples = []

  @params(apple=IApple)
  def add_apple(self, apple):
    self.apples.append(apple)
```

```
>>> tree = AppleTree()
>>> tree.add_apple('foo')
TypeError: Method argument 'apple' must be an instance of 'IApple'.
>>> from yuppy import Object
>>> class Apple(Object):
...   def get_color(self):
...     return 'red'
...   def get_weight(self):
...     return 1.0
...
>>> apple = Apple()
>>> tree.add_apple(apple)
>>> # success!
```

**Pull requests welcome!**

_Copyright (c) 2013 Jordan Halterman_
