// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/containers/image/v5/copy"
	"github.com/containers/image/v5/signature"
	"github.com/containers/image/v5/transports/alltransports"
	"github.com/sirupsen/logrus"

	"github.com/aws/aws-lambda-go/cfn"
	"github.com/aws/aws-lambda-go/lambda"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ecr"
	"github.com/aws/aws-sdk-go-v2/service/ecr/types"

	_ "cdk-ecr-deployment-handler/s3" // Install s3 transport plugin
)

const EnvLogLevel = "LOG_LEVEL"

func init() {
	s, exists := os.LookupEnv(EnvLogLevel)
	if !exists {
		logrus.SetLevel(logrus.InfoLevel)
	} else {
		lvl, err := logrus.ParseLevel(s)
		if err != nil {
			logrus.Errorf("error parsing %s: %v", EnvLogLevel, err)
		}
		logrus.SetLevel(lvl)
	}
}

func deleteImages(ctx context.Context, cfg aws.Config, repoName string, tags []string) (err error) {
	imageIDs := make([]types.ImageIdentifier, len(tags))
	for i := 0; i < len(tags); i++ {
		imageIDs[i] = types.ImageIdentifier{ImageTag: &tags[i]}
	}
	ecrService := ecr.NewFromConfig(cfg)
	_, err = ecrService.BatchDeleteImage(ctx, &ecr.BatchDeleteImageInput{
		RepositoryName: &repoName,
		ImageIds:       imageIDs,
	})
	if err != nil {
		log.Printf("Batch Delete Image Failed")
		log.Printf(err.Error())
	}
	_, err = ecrService.DeleteRepository(ctx, &ecr.DeleteRepositoryInput{
		RepositoryName: &repoName,
		Force:          true,
	})
	if err != nil {
		log.Printf("Delete Repository Failed")
		log.Printf(err.Error())
	}
	return err
}

func handler(ctx context.Context, event cfn.Event) (physicalResourceID string, data map[string]interface{}, err error) {
	physicalResourceID = event.PhysicalResourceID
	data = make(map[string]interface{})
	log.Printf("==========new handler------------")
	log.Printf("Event: %s", Dumps(event))

	if event.RequestType == cfn.RequestDelete {
		log.Printf("==========delete------------")
		cfg, err := config.LoadDefaultConfig(ctx)
		if err != nil {
			log.Printf("==========delete failed------------")
			log.Printf(err.Error())
			return physicalResourceID, data, err
		}
		imageTags := []string{"latest"}
		log.Printf("==========delete latest ai-solution-kit-sr------------")
		repositoryName, err := getStrProps(event.ResourceProperties, REPOSITORY_NAME)
		if err != nil {
			return physicalResourceID, data, err
		}
		deleteImages(ctx, cfg, repositoryName, imageTags)
		log.Printf("==========delete finished------------")
		return physicalResourceID, data, nil
	}
	if event.RequestType == cfn.RequestCreate || event.RequestType == cfn.RequestUpdate {
		srcImage, err := getStrProps(event.ResourceProperties, SRC_IMAGE)
		if err != nil {
			return physicalResourceID, data, err
		}
		destImage, err := getStrProps(event.ResourceProperties, DEST_IMAGE)
		if err != nil {
			return physicalResourceID, data, err
		}
		srcCreds, err := getStrPropsDefault(event.ResourceProperties, SRC_CREDS, "")
		if err != nil {
			return physicalResourceID, data, err
		}
		destCreds, err := getStrPropsDefault(event.ResourceProperties, DEST_CREDS, "")
		if err != nil {
			return physicalResourceID, data, err
		}

		log.Printf("SrcImage: %v DestImage: %v", srcImage, destImage)

		srcRef, err := alltransports.ParseImageName(srcImage)
		if err != nil {
			return physicalResourceID, data, err
		}
		destRef, err := alltransports.ParseImageName(destImage)
		if err != nil {
			return physicalResourceID, data, err
		}

		srcOpts := NewImageOpts(srcImage)
		srcOpts.SetCreds(srcCreds)
		srcCtx, err := srcOpts.NewSystemContext()
		if err != nil {
			return physicalResourceID, data, err
		}
		destOpts := NewImageOpts(destImage)
		destOpts.SetCreds(destCreds)
		destCtx, err := destOpts.NewSystemContext()
		if err != nil {
			return physicalResourceID, data, err
		}

		ctx, cancel := newTimeoutContext()
		defer cancel()
		policyContext, err := newPolicyContext()
		if err != nil {
			return physicalResourceID, data, err
		}
		defer policyContext.Destroy()

		_, err = copy.Image(ctx, policyContext, destRef, srcRef, &copy.Options{
			ReportWriter:   os.Stdout,
			DestinationCtx: destCtx,
			SourceCtx:      srcCtx,
		})
		if err != nil {
			// log.Printf("Copy image failed: %v", err.Error())
			// return physicalResourceID, data, nil
			return physicalResourceID, data, fmt.Errorf("copy image failed: %s", err.Error())
		}
	}

	return physicalResourceID, data, nil
}

func main() {
	lambda.Start(cfn.LambdaWrap(handler))
}

func newTimeoutContext() (context.Context, context.CancelFunc) {
	ctx := context.Background()
	var cancel context.CancelFunc = func() {}
	return ctx, cancel
}

func newPolicyContext() (*signature.PolicyContext, error) {
	policy := &signature.Policy{Default: []signature.PolicyRequirement{signature.NewPRInsecureAcceptAnything()}}
	return signature.NewPolicyContext(policy)
}

func getStrProps(m map[string]interface{}, k string) (string, error) {
	v := m[k]
	val, ok := v.(string)
	if ok {
		return val, nil
	}
	return "", fmt.Errorf("can't get %v", k)
}

func getStrPropsDefault(m map[string]interface{}, k string, d string) (string, error) {
	v := m[k]
	if v == nil {
		return d, nil
	}
	val, ok := v.(string)
	if ok {
		return val, nil
	}
	return "", fmt.Errorf("can't get %v", k)
}
