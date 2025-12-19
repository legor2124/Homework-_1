from setuptools import setup, find_packages

setup(
    name="config-converter",
    version="1.0.0",
    description="Конвертер учебного конфигурационного языка в TOML",
    author="Ваше Имя",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        'tomlkit>=0.11.0',
    ],
    entry_points={
        'console_scripts': [
            'config-converter=cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
