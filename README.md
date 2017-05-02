## AMISearch - AWS Lambda Function to search for AMI IDs ##

* AMISearch is an AWS Lambda Function to return latest AMI ID given an AMI Name, Owner, VirtualizationType, and RootDeviceType.
* Python 3.6 runtime environment
* AWS Lambda comes in handy for an easy solution to obtain the latest AMI Id when provisioning EC2 instances in Cloudformation.

### How-To Use ###

#### Create a zip archive and upload to S3 bucket ####

* `amisearch.py` requires the `requests` python module to be included in the zip archive.
* I've included a script, `uploadtos3.sh`, That will create `amisearch.zip` with all dependencies included and upload it to your S3 bucket.

* Usage: 

```
./scripts/uploadtos3.sh s3://my-bucket/lambda/amisearch.zip
```

#### Use CloudFormation to create the AMISearch Lambda Function ####

Included is a cloudformation templates to create the lambda function and needed IAM role

* The included Cloudformation template will create a stack with an Output value accessed by Export Key, `amiSearch-arn`.  The exported key provides the ARN value to the lambda function.  Use the Cloudformation intrinsic function "Fn::ImportValue" to import this value.

* To create the cloudformation stack, first change to the `cfn/` directory

```
cd cfn/
```

* Edit parameters.json for the correct bucket and key values

```
[                                                                                                                                                     
  {
    "ParameterKey": "S3Bucket",
    "ParameterValue": "my-bucket"
  },
  {
    "ParameterKey": "S3Key",
    "ParameterValue": "lambda/amisearch.zip"
  }
]
```

* Create the cloudformation stack after updating `parameters.json`.  Below is an example using `awscli`:

```
aws cloudformation create-stack --stack-name amiSearchStack --template-body file://amisearchstack.json --parameters file://parameters.json --capabilities CAPABILITY_IAM
```

#### Example Usage of AMISearch Lambda Function in Cloudformation ####

  If my provided cloudformation template to create the lambda function was utilizied, there will be a Cloudformation Output/Export Key called `amiSearch-arn` which returns the value of the ARN for the lambda function.  
  
  Below is an example Cloudformation template that creates an EC2 instance.  The below example uses the the amisearch AWS Lambda function to provide the latest AMI ID for Ubuntu Zesty with virtualization type of 'hvm' and root device type of 'ebs'.

```
   "AMISearch":{
      "Type": "Custom::AMISearch",
      "Properties": {
        "ServiceToken": { "Fn::ImportValue" : "amiSearch-arn" },
        "Name": "*ubuntu-zesty-daily-amd64-server-*",
        "Owner": "099720109477",
        "Region": "us-east-1",
        "VirtualizationType": "hvm",
        "RootDeviceType": "ebs"
      }
    },
    "myInstance" : {
      "Type" : "AWS::EC2::Instance",
      "Properties" : {
        "ImageId" : { "Fn::GetAtt" : ["AMISearch", "ImageId"] },
        "InstanceType": "t2.micro",
        ...
        ...
        ...
```

* Notice in the above example we create a "Custom" type which references our Lambda function by the `ServiceToken` Property.  For the `ServiceToken` property, use "Fn::ImportValue" to import the ARN value of the Lambda function.  The other properties we use to specify "Name", "Owner", "Region", "VirtualizationType", and "RootDeviceType" of the image.  All 5 Properties are required for the lambda function to work.

* When we create the EC2 instance, "myInstance", we use { "Fn::GetAtt" : ["AMISearch", "ImageId"] } to provide the AMI ID that the Lambda function returned.
