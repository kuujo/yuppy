Extreme Python
--------------

**Warning: Some developers may find this project deeply offensive. Please
use with caution.**

Extreme Python is a small library that adds _extreme_ features to Python
such as type checking of class variables and member access modifiers.
Sure, most Python developers frown on such features, but contrary to
popular belief there is a time and place for duck typing and lax access
restrictions, and that time and place is not always right here right now.
So for those other times and places, XPy can be used to add stability
and readability to your code with the same type checking and access
modifiers common to other object-oriented languages.

### Example
XPy is easy to use, implementing common object-oriented programming
features in a manner that is consistent with implementations in other
languages, making for more clear, concise, and reliable code.
```python
>>> from xpy import *
>>>
>>> class Foo(Object):
...   """A sample XPy object."""
...   foo = public(type=int)
...   bar = private(type=str)
...   baz = const('foobarbaz')
...   def __init__(self, foo, bar):
...     self.foo = foo
...     self.bar = bar
...   @public
...   def public_foo(self):
...     return self.bar
...   @private
...   def private_bar(self):
...     return self.foo
...   @protected
...   def protected_baz(self):
...     return self.bar
...
>>> foo = Foo(1, 'two')
>>> foo.foo
1
>>> foo.bar
AttributeError()
>>> foo.baz
foobarbaz
>>> foo.baz = 'bazbarfoo'
AttributeError()
>>> foo.public_foo()
two
>>> foo.private_bar()
AttributeError()
>>> bar = Foo('two', 3)
AttributeError()
>>> Baz(Foo):
...   pass
...
>>> baz = Baz(3, 'four')
>>> baz.protected_baz()
two
```
