
# Running Python tests

This directory contains model tests written in Python. They rely on the pytest testing framework.

## Install pytest

If you don't have pytest installed you can install it with:
```
$ sudo easy_install pytest
```
or, if you don't have sudo rights,
```
$ easy_install --user pytest
```

If you don't have easy_install, you can install that with:
```
$ wget https://bootstrap.pypa.io/ez_setup.py
$ sudo python ez_setup.py
```
or
```
$ wget https://bootstrap.pypa.io/ez_setup.py
$ python ez_setup.py --user
```
If you use the --user options above then binaries and packages will be installed to $HOME/.local/bin and $HOME/.local/lib . You may need to include these directories in your $PATH and $PYTHONPATH if they are not already.

## Run the tests

Then you can run the tests with:
```
$ py.test
```
Or a subset of the tests with:
```
$ py.test <test_file.py>
```
Also see:
```
$ py.test --help
```
Pay particular attention to the 'custom options' section.

If you don't have py.test installed on your machine, then you can do all of the above by replacing py.test with: python runtest.py
