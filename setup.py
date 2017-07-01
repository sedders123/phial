from setuptools import setup

setup(
    name='phial',
    version='0.1.0',
    url='https://github.com/sedders123/phial/',
    license='MIT',
    author='James Seden Smith',
    author_email='sedders123@gmail.com',
    description='A slack bot framework',
    packages=['phial'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'slackclient==1.0.6',
        'Werkzeug==0.12.2',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
