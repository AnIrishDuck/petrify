set -e

python setup.py install
for e in $(find examples -type f -name "*.py") ; do python $e ; done
