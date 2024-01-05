from setuptools import setup, find_packages

setup(
    name='OandaBot',
    version='1.0.2',
    description='OandaBot  is a professional trading bot that can be used to interact with the Stellar network.',
    author='nguemechieu',
    author_email='nguemechieu@live.com',
    packages=find_packages( '.'),
    install_requires=[
        'requirements.txt'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
          'OandaBot = OandaBot.OandaBot:main'
        ]
    },
     include_package_data=True,
     classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules'
     ],
     python_requires='>=3.12',
     keywords='run',
     url='https://github.com/nguemechieu/OandaBot',
     project_urls={
        'Bug Reports': 'https://github.com/nguemechieu/OandaBot/issues',
        'Source': 'https://github.com/nguemechieu/OandaBot'}

)