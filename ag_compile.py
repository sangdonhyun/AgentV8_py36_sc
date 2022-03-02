import py_compile
import glob
import os
py_list = glob.glob('*.py')

print(py_list)
py_list.remove('ag_compile.py')
for py in py_list:
    print(py)
    py_compile.compile((py))


