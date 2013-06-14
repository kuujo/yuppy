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
```

### API

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
public([value=None[, default=None[, type=None[, validate=None]]]])
```

#### private
Creates a private attribute. Note that if an attribute (`var`, `const`, or
`method`) is not passed as the first argument, this decorator will create
a private `method` if the argument is a `FunctionType`, or `var` otherwise.
```
public([value=None[, default=None[, type=None[, validate=None]]]])
```

#### static
Creates a static attribute. Note that if an attribute (`var`, `const`, or
`method`) is not passed as the first argument, this decorator will create
a public static `method` if the argument is a `FunctionType`, or `var`
otherwise.
```
public([value=None[, default=None[, type=None[, validate=None]]]])
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
  weight = private(type=float)

  def __init__(self, weight):
    self.weight = weight
```

Now, if we create an `Apple` instance we can see how the validation works.
Note that if an improper value is passed to the constructor, the validator
will automatically try to cast it to the correct type if only one type
is provided.

```python
>>> apple = Apple(1)
>>> apple.weight
AttributeError: Cannot access private Apple object member weight.
>>> apple = Apple('one')
AttributeError: Invalid attribute value for weight.
```
