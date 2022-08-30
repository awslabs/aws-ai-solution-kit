#!/usr/bin/env bash
cd deployment
./build-s3-dist.sh aws-gcr-solutions-workshop ai-solution-kit v1.0.0
cd ..
./copy.sh aws-gcr-solutions-workshop ai-solution-kit v1.0.0