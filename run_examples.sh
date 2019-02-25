set -e

python setup.py install
for e in $(find examples -type f) ; do python $e ; done
