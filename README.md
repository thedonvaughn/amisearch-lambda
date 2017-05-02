# AMISearch Lambda Function #

* AMISearch Lambda Function to return latest AMI ID given AMI Name, Owner, VirtualizationType, and RootDeviceType properties.
* Python 3.6 runtime environment
* AWS Lambda comes handy for an easy solution to obtain the latest AMI Id.
* Use this lambda function with Cloudformation stacks when provisioning EC2 instances

## Setup ##

### Create a zip archive of `amisearch.py` and `requests` module.  Upload the zip to S3 bucket ###

* I've included a script, `uploadtos3.sh`, that will create the `amisearch.zip` archive and upload to your S3 bucket.

* Usage: 

```
./scripts/uploadtos3.sh s3://my-bucket/lambda/amisearch.zip
```

### Use CloudFormation to create the AMISearch Lambda Function ###

* I've included a cloudformation stack to create the lambda function and needed IAM role for permissions
* The included stack will create a CloudFormation an Output value with the Export Key `amiSearch-arn`.  The export key provides the ARN to the lambda function.  You can use the Cloudformation intrinsic function "Fn::ImportValue" to import this value.

* To create the stack, first change to the `cfn/` directory

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

* Create the cloudformation stack however you wish.  Below is an example using `awscli`:

```
aws cloudformation create-stack --stack-name amiSearchStack --template-body file://amisearchstack.json --parameters file://parameters.json --capabilities CAPABILITY_IAM
```

### Example Usage of AMISearch Lambda Function in Cloudformation ###

* If you've used my provided cloudformation template to create the amisearch function, there will be an Export Key called `amiSearch-arn` which holds the value of the ARN for the lambda function.  Below is an example Cloudformation template that creates an EC2 instance using the AMISearch Lambda function to dynamically provide the latest AMI ID for Ubuntu Zesty with virtualization type of 'hvm' and root device type of 'ebs'.

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
			...
			...
			...
```

* Notice in the above example we create a "Custom::AMISearch" type.  We use "Fn::ImportValue" to provide the ARN to the AMISearch Lambda function for the "ServiceToken" property.   We have to specify "Name", "Owner", "Region", "VirtualizationType", and "RootDeviceType" Properties for the function to work.

* When we create the EC2 instance, "myInstance", we use { "Fn::GetAtt" : ["AMISearch", "ImageId"] } to provide the AMI ID that the Lambda function returned.
