from setuptools import setup

setup(name='mistletoe',
      version='0.1',
      description='A fast, extensible Markdown parser in pure Python.',
      url='https://github.com/miyuchina/mistletoe',
      author='Mi Yu',
      author_email='hello@afteryu.me',
      license='GNU GPLv3',
      packages=['mistletoe'],
      entry_points={'console_scripts': ['mistletoe = mistletoe.__main__:main']},
      python_requires='~=3.5',
      zip_safe=False)
