from setuptools import setup

setup(
    name='phial-slack',
    version='0.1.0',
    url='https://github.com/sedders123/phial/',
    license='MIT',
    author='James Seden Smith',
    author_email='sedders123@gmail.com',
    description='A Slack bot framework',
    long_description=open('README.rst').read(),
    packages=['phial'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.6',
    keywords=['Slack', 'bot', 'Slackbot'],
    install_requires=[
        'slackclient==1.0.6',
        'Werkzeug==0.12.2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
