from setuptools import setup
from setuptools.command.test import test as TestCommand
import csmash

requirements = [
    'PasteDeploy'
]

test_requirements = [
    'virtualenv == 1.7.1.2',
    'tox == 1.3',
    'pytest == 2.2.4',
    'pylint == 0.25.1',
    'pytest-pep8 == 0.8',
]


class ToxTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        from pylint.lint import Run
        Run(['csmash', '--reports=n', '--include-ids=y'], exit=False)
        import tox
        tox.cmdline(args=[])


setup(
    name="configsmash",
    version=csmash.__version__,
    author="Robby Ranshous",
    author_email="rranshous@gmail.com",
    description=("python lib / script for reading"
    " cascading sets of ini files"),
    keywords="configuration",
    url="https://github.com/rranshous/configsmash",
    py_modules=["csmash"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
    ],
    install_requires=requirements,
    tests_require=test_requirements,
    cmdclass={
        'test': ToxTest,
    },
    entry_points={
        'console_scripts': [
            'csmash = csmash:cli',
        ]
    },
)
