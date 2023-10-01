from setuptools import find_packages
from setuptools import setup

setup(
    name='stt_asterisk',
    version='1.1',
    description='Get a transcript of a call in Asterisk',
    author='Jorge Sisco',
    author_email='jorgesisco17@gmail.com',
    url='https://github.com/jorgesisco/stt_asterisk',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'ari-stasis = stt.ari_stasis:main',
            'ari-server = stt.ari_server:main',
            'call-transcript = stt.app:main',
        ],
    },
    install_requires=[
        'ari @ git+https://github.com/jorgesisco/ari-py.git@main',
    ],
)
