__version__ = '0.1.0'

from setuptools import setup

if __name__ == '__main__':
  setup(
    name='Extreme Python',
    description='Takes Python programming to the extreme!',
    author='Jordan Halterman',
    version=__version__,
    author_email='jordan.halterman@gmail.com',
    url='https://github.com/jordanhalterman/extreme-python',
    keywords=['extreme', 'oop'],
    py_modules=['xpy'],
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
