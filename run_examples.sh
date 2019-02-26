set -e

python setup.py install
mkdir output
for e in $(find examples -type f) ; do python $e ; done
