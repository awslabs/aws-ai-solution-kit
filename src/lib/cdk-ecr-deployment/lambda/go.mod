module cdk-ecr-deployment-handler

go 1.15

require (
	github.com/aws/aws-lambda-go v1.23.0
	github.com/aws/aws-sdk-go-v2 v1.3.2
	github.com/aws/aws-sdk-go-v2/config v1.1.6
	github.com/aws/aws-sdk-go-v2/service/ecr v1.2.2
	github.com/aws/aws-sdk-go-v2/service/s3 v1.5.0
	github.com/containerd/containerd v1.6.26 // indirect
	github.com/containers/image/v5 v5.17.0
	github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da
	github.com/opencontainers/go-digest v1.0.0
	github.com/pkg/errors v0.9.1
	github.com/sirupsen/logrus v1.9.3
	github.com/stretchr/testify v1.8.4
)
