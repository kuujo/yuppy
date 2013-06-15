__version__ = '0.1.1'

from setuptools import setup

if __name__ == '__main__':
  setup(
    name='Yuppy',
    description='Python interfaces and data encapsulation.',
    author='Jordan Halterman',
    version=__version__,
    author_email='jordan.halterman@gmail.com',
    url='https://github.com/jordanhalterman/yuppy',
    keywords=['yuppy', 'oop', 'interfaces', 'encapsulation'],
    py_modules=['yuppy'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.5',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Natural Language :: English',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ])
