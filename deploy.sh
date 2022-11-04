#!/bin/bash -e
#
# Upload snowflake-ingest-python Package to PyPI
#
# USAGE ./deploy.sh <pypi_username> <pypi_password>

echo $WORKSPACE

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo $THIS_DIR
function upload_package() {
    local target_pkg=ingest

    rm -f $THIS_DIR/dist/snowflake_${target_pkg}*.whl ||  true
    rm -f $THIS_DIR/snowflake/${target_pkg}/generated_version.py || true
    rm -rf $THIS_DIR/snowflake/${target_pkg}/build || true
    rm -f $THIS_DIR/dist/snowflake{_,-}${target_pkg}*.{whl,tar.gz} || true

    python3 setup.py sdist bdist_wheel

    
    WHL=$(ls $WORKSPACE/dist/snowflake_${target_pkg}*.whl)
    TGZ=$(ls $WORKSPACE/dist/snowflake_${target_pkg}*.tar.gz)

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

which python3
python3 --version


virtualenv -p python3 release

source release/bin/activate
pip3 install --upgrade pip
pip3 install -U setuptools_rust setuptools twine 

touch pypirc
#!/bin/bash -ex
export TERM=vt100

cat >$WORKSPACE/pypirc <<PYPIRC
[distutils]
index-servers =
  pypi

[pypi]
username:$pypi_user
password:$pypi_password
PYPIRC
export CRYPTOGRAPHY_DONT_BUILD_RUST=1
export TWINE_CONFIG_FILE=$WORKSPACE/pypirc


upload_package
deactivate
