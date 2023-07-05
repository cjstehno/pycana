
from setuptools import setup, find_packages

setup(
    name='pycana',
    version='0.0.2',
    description='Spell searching tool.',
    long_description='Spell searching tool.',
    long_description_content_type='text/markdown',
    author='Christopher J. Stehno',
    author_email='chris.stehno@gmail.com',
    url='https://github.io/cjstehno/pycana',
    license='unlicensed',
    packages=find_packages(exclude=['tests*']),
    # package_data={'todo': ['templates/*']},
    # include_package_data=True,
    entry_points="""
        [console_scripts]
        pycana = pycana.main:main
    """,
    install_requires=[
        'click',
        'rich',
    ],
)
