#!/usr/bin/env bash

export DIST_OUTPUT_BUCKET=$1
export SOLUTION_NAME=$2
export VERSION=$3

if [ -d "deployment/regional-s3-assets/" ]; then
    #echo "Copy regional assets"
    #echo "$REGIONS" | xargs -n1 | xargs -t -I {} aws s3 cp deployment/regional-s3-assets/ s3://$DIST_OUTPUT_BUCKET-{}/$SOLUTION_NAME/$VERSION/ --region {} --recursive --acl public-read

    echo "Copy global assets to China region"
    echo "cn-north-1 cn-northwest-1" | xargs -n1 | \
    xargs -t -I {} aws s3 cp deployment/regional-s3-assets/ s3://$DIST_OUTPUT_BUCKET-{}/$SOLUTION_NAME/$VERSION/ --region {} --recursive --acl public-read --profile workshop-cn
fi

echo "Copy global s3 assets to Global region & China region"
#aws s3 cp deployment/global-s3-assets/ s3://$DIST_OUTPUT_BUCKET/$SOLUTION_NAME/$VERSION/ --recursive --acl public-read --profile workshop-g
aws s3 cp deployment/global-s3-assets/ s3://$DIST_OUTPUT_BUCKET/$SOLUTION_NAME/$VERSION/ --recursive --acl public-read --profile workshop-cn