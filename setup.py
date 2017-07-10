#!/usr/bin/env python

from setuptools import setup
from setuptools.command.test import test as TestCommand


# Inspired by the example at https://pytest.org/latest/goodpractises.html
class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])


setup(name='monon',
      version='1.0',
      description='Money and Currency library',
      author='Pedro Burón',
      author_email='pedroburonv@gmail.com',
      url='https://github.com/pedroburon',
      packages=['monon'],
      setup_requires=[
        'nose==1.3.7',
        'coverage==4.4.1'
      ],
      cmdclass={'test': NoseTestCommand},
     )

