#!/bin/sh

set -e

cd $(dirname $0)

version=$(python -c 'import yassh; print yassh.__version__')

rm -rf dist/*
python setup.py sdist bdist_wheel

while true; do
    read -p "Do you wish to upload ${version} to pypi.python.org [Yn] ?" yn
    yn=${yn:-y}
    case $yn in
        [Yy])
            twine upload dist/*
            git tag v${version}
            git push origin v${version}
            break
            ;;
        [Nn])
            break
            ;;
        *)
            echo "Please answer yes or no."
            ;;
    esac
done

