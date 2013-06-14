Extreme Python
--------------

Extreme Python is a small library that integrates seamlessly with Python
to promote data integrity through essential principles of object-oriented
programming. XPy adds authentic Python support for encapsulation and
arbitrary object member validation - features that are commonly found
in other object-oriented languages. While should certainly not always
be used when developing with Python, it can certainly improve the
integrity of your data and the stability of your code where the natural
flexibility of Python is not required..

##### _"But encapsulation is bad!"_
But options are good. Sure, Python is a dynamic language, and often its
flexibility can be used to creatively conquer complex problems (indeed,
XPy was developed using many of these features). But lax access
restrictions are not _always_ beneficial. XPy can help protect the
integrity of your data by preventing important internal instance data
from being changed.

##### _"What about type checking then!?"_
Sure, duck typing often allows for more flexibility for users of libaries.
But without the proper precautions a lack of type checking can ultimately
lead to unpredictable code. What if some code somewhere is changing your
FTP class's `port` attribute to an invalid string? Guess what, you won't
find out about it until your code tries to connect to the FTP server. By
that time, it's hard to tell where that bad port number came from. XPy
can automatically type check class or instance variables _at the point
at which they are set_ to ensure that your data is not corrupted.

### A Complete Example
XPy is easy to use, implementing common object-oriented programming
features in a manner that is consistent with implementations in other
languages, making for more clear, concise, and reliable code.

```python
# When importing xpy.*, the following variables will be imported:
# Object, var, const, method, public, protected, private, and static.
from xpy import *

# XPy classes *must* extend the base xpy.Object class.
class Apple(Object):
  """An abstract apple."""
  weight = private(type=float)

  def __init__(self, weight):
    self.weight = weight

  @protected
  def get_weight(self):
    return self.weight

  @protected
  def set_weight(self, weight):
    self.weight = weight

class GreenApple(Object):
  """A green apple."""
  color = private(const('green'))

  def __init__(self, weight):
    # Green apples are .5 lbs heavier on average.
    self.override_weight(weight+.5)

  @private
  def override_weight(self, weight):
    return self.set_weight(weight)

  @public
  def get_weight(self):
    return self.weight

  @public
  def get_color(self):
    return self.color
```

#### Testing the example
```python
>>> apple = Apple('two')
AttributeError: Invalid attribute value for 'weight'.
>>> apple = Apple(2.0)
>>> apple.set_weight(2.5)
AttributeError: Cannot access protected Apple attribute 'set_weight'.
>>> apple.get_weight()
AttributeError: Cannot access protected Apple attribute 'get_weight'.
>>> greenapple = GreenApple(2.0)
>>> greenapple.color
AttributeError: Cannot access private GreenApple attribute 'color'.
>>> greenapple.get_color()
green
>>> greenapple.get_weight()
2.5
>>> greenapple.set_weight()
AttributeError: Cannot access protected GreenApple attribute 'set_weight'.
```

### The API

#### var
Creates a public variable attribute.
```
var([default=None[, type=None[, validate=None]]])
```

#### const
Creates a public constant attribute.
```
const(value)
```

#### method
Creates a public method attribute.
```
method(callback)
```

#### public
Creates a public attribute. Note that if an attribute (`var`, `const`, or
`method`) is not passed as the first argument, this decorator will create
a public `method` if the argument is a `FunctionType`, or `var` otherwise.
```
public([value=None[, default=None[, type=None[, validate=None]]]])
```

#### protected
Creates a protected attribute. Note that if an attribute (`var`, `const`, or
`method`) is not passed as the first argument, this decorator will create
a protected `method` if the argument is a `FunctionType`, or `var` otherwise.
```
protected([value=None[, default=None[, type=None[, validate=None]]]])
```

#### private
Creates a private attribute. Note that if an attribute (`var`, `const`, or
`method`) is not passed as the first argument, this decorator will create
a private `method` if the argument is a `FunctionType`, or `var` otherwise.
```
private([value=None[, default=None[, type=None[, validate=None]]]])
```

#### static
Creates a static attribute. Note that if an attribute (`var`, `const`, or
`method`) is not passed as the first argument, this decorator will create
a public static `method` if the argument is a `FunctionType`, or `var`
otherwise.
```
static([value=None[, default=None[, type=None[, validate=None]]]])
```

### Examples

#### Type Validation
XPy can perform direct type checking and arbitrary execution of validation
callbacks. When a mutable XPy attribute is set, validators will automatically
be executed. This ensures that values are validated at the time they're
set rather than when they're accessed.

Any `var` type can perform data validation. When creating a new `var`,
we can pass either `type=[type]` or `validate=[validator]` to the object
constructor.

```python
from xpy import *

class Apple(Object):
  """An abstract apple."""
  weight = var(type=float)

  def __init__(self, weight):
    self.weight = weight
```

Now, if we create an `Apple` instance we can see how the validation works.
Note that if an improper value is passed to the constructor, the validator
will automatically try to cast it to the correct type if only one type
is provided.

```python
>>> apple = Apple(1)
>>> apple = Apple('one')
AttributeError: Invalid attribute value for 'weight'.
```

#### Private Members
Private members are variables that can only be accessed from within a class.
They support data integrity by preventing class users from altering internal attribute.
With XPy we can decorate any class member with `private` to hide it from outside access.
Note that XPy variables must be defined within the class definition, not
arbitrarily defined within class code. This is common in other object-oriented
languages as well.

```python
from xpy import *

class Apple(Object):
  """An abstract apple."""
  weight = private(type=float, default=None)

  def __init__(self, weight):
    self.weight = weight

  @private
  def _get_weight(self):
    return self.weight

  def get_weight(self):
    return self._get_weight()
```

Now, if we create a new `Apple` instance and try to access its attributes
from outside the class we will fail. However, we'll see that access from
within the class works just fine.

```python
>>> apple = Apple(2.5)
>>> apple.weight
AttributeError: Cannot access private Apple object member 'weight'.
>>> apple._get_weight()
AttributeError: Cannot access private Apple object member '_get_weight'.
>>> apple.get_weight()
2.5
```

#### Protected Members
_Note that protected member _variables_ are not currently reliable. Thus
the `protected` decorator should only be used for methods._

Protected members are variables that can be accessed only from within a
class or a sub-class of the declaring class. Thus, while protected
members have more relaxed access restriction, values are still hidden
from outside users. With XPy we can use the `protected` decorator to
declare any class member protected.

```python
from xpy import *

class Apple(Object):
  """An abstract apple."""
  weight = private(type=float, default=None)

  def __init__(self, weight):
    self.weight = weight

  @protected
  def _get_weight(self):
    return self.weight

class GreenApple(Apple):
  """A green apple."""
  @public
  def get_weight(self):
    return self._get_weight()
```

With this interface, we can access `Apple.weight` through `GreenApple.get_weight()`.
This is because `GreenApple` has access to the `Apple._get_weight()` method
which subsequently has access to the private `Apple.weight` attribute.

```python
>>> apple = GreenApple(2.5)
>>> apple.weight
AttributeError: GreenApple object has not attribute 'weight'.
>>> apple._get_weight()
AttributeError: Cannot access protected GreenApple object member '_get_weight'.
>>> apple.get_weight()
2.5
```

#### Static Members
Static XPy members are equivalent to standard Python class members. This is
essentially the same parallel that exists between Python's class members
and static variables in many other object-oriented languages. With XPy we
can use the `static` decorator to create static methods or properties. Note
that `static` members can be further decorated with `public`, `private`,
or `protected`.

```python
from xpy import *

class Apple(Object):
  """An abstract apple."""
  weight = static(type=float, default=None)
```

With static members, changes to a member variable will be applied to
all instances of the class. So, even after instantiating a new instance
of the class, the `weight` attribute value will remain the same.

```python
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

#### Constants
Constants are attributes which have a permanent value. They can be used for
any value which should never change within the application, such as an
application port number, for instance. With XPy we can use the `const`
decorator to create a constant, passing a single permanent value to the
constructor.

```python
from xpy import *

class Apple(Object):
  """An abstract apple."""
  weight = const(2.5)
```

Now, all apple weights are set at a constant `2.5`, and any attempts to
change that value will result in an `AttributeError`.

```python
>>> apple = Apple(2.5)
>>> apple.weight
2.5
>>> apple.weight = 2.0
AttributeError: Cannot override Apple object constant 'weight'.
```
