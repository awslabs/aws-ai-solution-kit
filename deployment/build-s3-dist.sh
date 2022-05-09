#!/bin/bash
# This assumes all of the OS-level configuration has been completed and git repo has already been cloned
#
# This script should be run from the repo's deployment directory
# cd deployment
# ./build-s3-dist.sh
#
# Check to see if input has been provided:
# if [ "$1" ]; then
#     echo "Usage: ./build-s3-dist.sh"
#     exit 1
# fi

set -e

title() {
    echo "------------------------------------------------------------------------------"
    echo $*
    echo "------------------------------------------------------------------------------"
}

run() {
    >&2 echo ::$*
    $*
}


# Get reference for all important folders
template_dir="$PWD"
source_dir="$template_dir/../src"
lib_dir="$template_dir/../lib"
build_dist_dir="$lib_dir/lambda-assets"


echo "------------------------------------------------------------------------------"
echo "[Init] Clean existed dist folders"
echo "------------------------------------------------------------------------------"

echo "rm -rf $build_dist_dir"
rm -rf $build_dist_dir
echo "mkdir -p $build_dist_dir"
mkdir -p $build_dist_dir

echo "------------------------------------------------------------------------------"
echo "cdk synth"
echo "------------------------------------------------------------------------------"
cd ${template_dir}
__dir="$(cd "$(dirname $0)";pwd)"
SRC_PATH="${__dir}/../src"
CDK_OUT_PATH="${__dir}/../cdk.out"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Parameters not enough"
    echo "Example: $(basename $0) <BUCKET_NAME> <SOLUTION_NAME> [VERSION]"
    exit 1
fi

export BUCKET_NAME=$1
export SOLUTION_NAME=$2
export GLOBAL_S3_ASSETS_PATH="${__dir}/global-s3-assets"
export REGIONAL_S3_ASSETS_PATH="${__dir}/regional-s3-assets"



title "init env"

run rm -rf ${GLOBAL_S3_ASSETS_PATH} && run mkdir -p ${GLOBAL_S3_ASSETS_PATH}
run rm -rf ${REGIONAL_S3_ASSETS_PATH} && run mkdir -p ${REGIONAL_S3_ASSETS_PATH}
run rm -rf ${CDK_OUT_PATH}

if [ -z "$3" ]; then
    export VERSION=$(git describe --tags || echo latest)
    echo "BUCKET_NAME=${BUCKET_NAME}"
    echo "SOLUTION_NAME=${SOLUTION_NAME}"
    echo "VERSION=${VERSION}"

else
    export VERSION=$3
fi

echo "${VERSION}" > ${GLOBAL_S3_ASSETS_PATH}/version

cd ..
run yarn install --check-files --frozen-lockfile
if [ -z "${BUILD_CONTAINER}" ]; then
    run yarn build
else
    run yarn build-containers
fi

export USE_BSS=true
# How to config https://github.com/wchaws/cdk-bootstrapless-synthesizer/blob/main/API.md
export BSS_TEMPLATE_BUCKET_NAME="${BUCKET_NAME}"
export BSS_FILE_ASSET_BUCKET_NAME="${BUCKET_NAME}-\${AWS::Region}"
export BSS_FILE_ASSET_PREFIX="${SOLUTION_NAME}/${VERSION}/"
export BSS_FILE_ASSET_REGION_SET="us-east-1,${BSS_FILE_ASSET_REGION_SET}"

run npm run synth -- --output ${CDK_OUT_PATH}

# taskcat
echo "----taskcat start----"
if [ "$3" ] && [ "$3" == "TASKCAT" ]; then
    pip install taskcat
    taskcat test run 
fi

echo "${VERSION}" > ${GLOBAL_S3_ASSETS_PATH}/version
run ${__dir}/helper.py ${CDK_OUT_PATH}
cp -r deployment/ ../../deployment/