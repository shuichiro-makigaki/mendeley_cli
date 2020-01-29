from pathlib import Path
from setuptools import setup, find_packages

setup(
    name='mendeley_cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/shuichiro-makigaki/mendeley_cli',
    license='MIT',
    author='Shuichiro MAKIGAKI',
    author_email='shuichiro.makigaki@gmail.com',
    description='Mendeley CLI',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    entry_points='''
        [console_scripts]
        mendeley=mendeley_cli:cmd
    ''',
)
