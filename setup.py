from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

test_deps = [
    "pytest",
]

extras = {
    "test": test_deps,
}

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="toggler",
    use_scm_version=True,
    description="Feature Flags Manager",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Versada (Andrius Laukavičius)",
    author_email="andrius.laukavicius@versada.eu",
    url="https://github.com/versada/toggler",
    license="LGPLv3",
    packages=find_packages(),
    tests_require=test_deps,
    extras_require=extras,
    setup_requires=[
        "setuptools_scm",
    ],
    install_requires=install_requires,
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
