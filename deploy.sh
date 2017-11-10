#!/bin/bash -e
#
# Upload snowflake-ingest-python Package to PyPI
#
# USAGE ./deploy.sh <pypi_username> <pypi_password>
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function upload_package() {
    local target_pkg=ingest

    rm -f $THIS_DIR/dist/snowflake_${target_pkg}*.whl ||  true
    rm -f $THIS_DIR/snowflake/${target_pkg}/generated_version.py || true
    rm -rf $THIS_DIR/snowflake/${target_pkg}/build || true
    rm -f $THIS_DIR/dist/snowflake{_,-}${target_pkg}*.{whl,tar.gz} || true

    python setup.py sdist bdist_wheel

    WHL=$(ls $THIS_DIR/dist/snowflake_${target_pkg}*.whl)
    TGZ=$(ls $THIS_DIR/dist/snowflake_${target_pkg}*.tar.gz)

    VIRTUAL_ENV_DIR=$THIS_DIR/upload
    echo "****** $WHL ******"
    echo
    unzip -l $WHL
    echo
    echo "****** $TGZ ******"
    echo
    tar tvfz $TGZ
    echo "Verify the package contents. DON'T include any test case or data!"
    if [[ -z "$JENKINS_URL" ]]; then
        # not-jenkins job
        read -n1 -p "Are you sure to upload $WHL (y/N)? "
        echo
        if [[ $REPLY != [yY] ]]; then
            log INFO "Good bye!"
            exit 0
        fi
    fi
    TWINE_OPTIONS=()
    if [[ -n "$TWINE_CONFIG_FILE" ]]; then
        TWINE_OPTIONS=("--config-file" "$TWINE_CONFIG_FILE")
    fi 
    # twine register -r pypi $WHL # one time
    twine upload ${TWINE_OPTIONS[@]} -r pypi $WHL
    twine upload ${TWINE_OPTIONS[@]} -r pypi $TGZ
}

virtualenv-3.4 upload
source upload/bin/activate
pip install -U pip setuptools twine

touch pypirc
cat >pypirc<< PYPIRC
[distutils] # this tells distutils what package indexes you can push to
index-servers =
  pypi
  pypitest

[pypi]
repository: https://upload.pypi.org/legacy/
username: $1
password: $2

[pypitest]
repository: https://test.pypi.org/legacy/
username: $1 
password: $2
PYPIRC
TWINE_CONFIG_FILE=$THIS_DIR/pypirc

upload_package
deactivate
