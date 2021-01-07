from os.path import dirname, join

from setuptools import setup

setup(
    name='validated-dc',
    version='1.3.0',
    license='BSD',
    author='Evgeniy Burdin',
    author_email='e.s.burdin@mail.ru',
    py_modules=['validated_dc'],
    description='Dataclass with data validation.',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url='https://github.com/EvgeniyBurdin/validated_dc',
    keywords='validated dataclasses typing dict api',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
    ],
    python_requires='>=3.7',
)
