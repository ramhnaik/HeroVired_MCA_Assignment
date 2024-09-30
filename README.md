# Graded Assignment on Monitoring, Scaling and Automation

### Develop a system that automatically manages the lifecycle of a web application hosted on  EC2 instances, monitors its health, and reacts to changes in traffic by scaling resources.  Furthermore, administrators receive notifications regarding the infrastructure's health and scaling events. 

## Steps:

### 1. Web Application Deployment:

#### Create an S3 bucket for static files:
~~~
import boto3
s3 = boto3.client('s3')
bucket_name = 'ramananda_s3_bucket'
s3.create_bucket(Bucket=bucket_name)
# Upload static files
s3.upload_file('/static_files/sample.txt', 'mybucket', 'sample.txt')
~~~

#### Launch an EC2 instance:
Use boto3 to launch an EC2 instance, configure it with a web server Nginx
~~~~
ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
    ImageId='ami-0e42b3cc568cd07e3',
    InstanceType='t4g.micro',
    KeyName='ramananda_key',
    SecurityGroupIds=['sg-057f0e6c8849c7ff8 (default)']
    MinCount=1,
    MaxCount=1,
    UserData='''#!/bin/bash
    sudo apt update
    sudo apt install nginx
    sudo systemctl start nginx
    echo "Hello World from $(hostname -f)" > /var/www/html/index.html
    '''  
)

instance_id = instance[0].id
~~~~

#### Deploy the web application:
Use the EC2 instance_id to SSH into the instance and deploy the application.This can be  automated  by copying files and using SSH/SFTP tools or integrate this step into the UserData script.

### 2. Load Balancing with Application Load Balancer (ALB):

#### Create an ALB using boto3:
Set up the Application Load Balancer (ALB) to handle traffic distribution across EC2 instances.

~~~
elb = boto3.client('elbv2')
load_balancer = elb.create_load_balancer(
    Name='ramananda-lb',
    Subnets=['subnet-03ca36de9a927fe8e', 'subnet-09bd0e0acc92d4efa'], 
    SecurityGroups=['sg-057f0e6c8849c7ff8 (default)']
)

lb_arn = load_balancer['LoadBalancers'][0]['LoadBalancerArn']
~~~

### Register EC2 instance with ALB:

~~~
elb.register_targets(
    TargetGroupArn='HTML-Prashant-b7-1',
    Targets=[{'Id': instance_id, 'Port': 80}],
    VpcId='vpc-0321f38a7b594180d'
)
~~~

### 3. Auto Scaling Group (ASG) Configuration:

#### Create an ASG with EC2 instances as a template:
Configure the ASG to use the EC2 instance template (Launch Configuration or Launch Template).
~~~
autoscaling = boto3.client('autoscaling')
response = autoscaling.create_auto_scaling_group(
    AutoScalingGroupName='my-web-app-asg',
    LaunchConfigurationName='my-launch-configuration',
    MinSize=1,
    MaxSize=5,
    DesiredCapacity=2,
    VPCZoneIdentifier='subnet-0123456789abcdef0,subnet-0987654321fedcba'
)

#### Configure scaling policies:
Set up scaling policies to adjust based on CloudWatch metrics like CPU utilization.

~~~
scaling_policy = autoscaling.put_scaling_policy(
    AutoScalingGroupName='my-web-app-asg',
    PolicyName='scale-up',
    AdjustmentType='ChangeInCapacity',
    ScalingAdjustment=1,
    Cooldown=300
)
~~~

### 4. SNS Notifications:
Set up SNS topics for health and scaling alerts:
Create SNS topics to send notifications when scaling events occur or if health checks fail.

~~~
sns = boto3.client('sns')
scaling_topic = sns.create_topic(Name='scaling-events')
health_topic = sns.create_topic(Name='health-alerts')

#Subscribe admins to receive notifications via email
sns.subscribe(TopicArn=scaling_topic['TopicArn'], Protocol='email', Endpoint='admin@example.com')
sns.subscribe(TopicArn=health_topic['TopicArn'], Protocol='email', Endpoint='admin@example.com')
~~~

#### Integrate SNS with Lambda for notifications:
You can set up Lambda functions triggered by Auto Scaling events or CloudWatch alarms to publish messages to SNS topics.

### 5. Infrastructure Automation:
Single script to manage the infrastructure:
Create a single Python script that automates deployment, updates, and teardown of the entire stack.
~~~
def deploy_infrastructure():
    # Create S3 bucket, launch EC2, configure ALB, set up ASG, SNS, etc.
    pass

def update_infrastructure():
    # Logic for updating the infrastructure
    pass

def teardown_infrastructure():
    # Logic for tearing down the infrastructure
    pass
~~~

### 6. Optional Enhancement – Dynamic Content Handling:
Store user-generated content on S3:
For uploads, temporarily store them on EC2 and move them to S3 with a background job or Lambda.

~~~
def move_to_s3(file_path, bucket_name):
    s3.upload_file(file_path, bucket_name, 'uploads/' + file_path)
~~~
