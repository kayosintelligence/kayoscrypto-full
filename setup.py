"""
KayosCrypto - Sistema de Criptografia com Filosofia Geométrica Bíblica
"""
from setuptools import setup, find_packages
import os

# Ler README
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Versão
VERSION = '5.0.1'

# Dependências
INSTALL_REQUIRES = [
    'numpy>=1.20.0',
]

EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'black>=22.0.0',
        'pylint>=2.15.0',
        'flake8>=5.0.0',
        'mypy>=0.990',
        'isort>=5.10.0',
    ],
    'security': [
        'bandit>=1.7.0',
        'safety>=2.0.0',
    ],
    'docs': [
        'sphinx>=5.0.0',
        'sphinx-rtd-theme>=1.0.0',
    ],
}

# All extras
EXTRAS_REQUIRE['all'] = list(set(sum(EXTRAS_REQUIRE.values(), [])))

setup(
    name='kayoscrypto',
    version=VERSION,
    description='Sistema de Criptografia com Filosofia Geométrica Bíblica',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='KAYOS Systems',
    author_email='security@kayoscrypto.dev',
    url='https://github.com/kayos-systems/kayoscrypto',
    project_urls={
        'Documentation': 'https://docs.kayoscrypto.dev',
        'Source': 'https://github.com/kayos-systems/kayoscrypto',
        'Tracker': 'https://github.com/kayos-systems/kayoscrypto/issues',
    },
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points={
        'console_scripts': [
            'kayoscrypto=cli.kayoscrypto_cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed',
    ],
    keywords=[
        'cryptography',
        'encryption',
        'security',
        'fibonacci',
        'geometric',
        'ezekiel',
        'philosophy',
        'enterprise',
    ],
    include_package_data=True,
    zip_safe=False,
)
