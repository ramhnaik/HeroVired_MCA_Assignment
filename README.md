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
    SecurityGroupIds=['sg-057f0e6c8849c7ff8']
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

### 2. Load Balancing with Application Load Balancer (ALB):

#### Create an ALB using boto3:
Set up the Application Load Balancer (ALB) to handle traffic distribution across EC2 instances.

~~~
elb = boto3.client('elbv2')
load_balancer = elb.create_load_balancer(
    Name='ramananda-lb',
    Subnets=['subnet-03ca36de9a927fe8e', 'subnet-09bd0e0acc92d4efa'], 
    SecurityGroups=['sg-057f0e6c8849c7ff8']
)

lb_arn = load_balancer['LoadBalancers'][0]['LoadBalancerArn']
~~~

#### Register EC2 instance with ALB:

~~~
elb.register_targets(
    TargetGroupArn='HTML-Prashant-b7-1',
    Targets=[{'Id': instance_id, 'Port': 80}],
    VpcId='vpc-0321f38a7b594180d'
)
~~~

### 3. Auto Scaling Group (ASG) Configuration

#### Create a Launch Template for the EC2 instance:

~~~
autoscaling = boto3.client('autoscaling')
response = autoscaling.create_launch_configuration(
    LaunchConfigurationName='web-app-launch-config',
    ImageId='ami-0e42b3cc568cd07e3',
    InstanceType='t4g.micro',
    KeyName='ramananda_key',
    SecurityGroups=['sg-057f0e6c8849c7ff8']
)
~~~

#### Create an Auto Scaling Group:
~~~
response = autoscaling.create_auto_scaling_group(
    AutoScalingGroupName='web-app-asg',
    LaunchConfigurationName='web-app-launch-config',
    MinSize=1,
    MaxSize=5,
    DesiredCapacity=2,
    VPCZoneIdentifier='subnet-0123456789abcdef0,subnet-0123456789abcdef1',
    TargetGroupARNs=['your-target-group-arn'],
)
~~~

#### Define Scaling Policies: Create scaling policies based on metrics like CPU utilization:

~~~
cloudwatch = boto3.client('cloudwatch')
scaling_policy = autoscaling.put_scaling_policy(
    AutoScalingGroupName='web-app-asg',
    PolicyName='ScaleOutPolicy',
    AdjustmentType='ChangeInCapacity',
    ScalingAdjustment=1,
    Cooldown=300
)
~~~

### 4. SNS Notifications

#### Create SNS Topic for Alerts:
~~~
sns = boto3.client('sns')
response = sns.create_topic(Name='scaling-alerts')
topic_arn = response['TopicArn']
~~~

#### Subscribe Admins to the Topic:
~~~
response = sns.subscribe(
    TopicArn=topic_arn,
    Protocol='email',
    Endpoint='ramhnaik@gmail.com'
)
~~~

#### Trigger SNS Notifications on Scaling Events: 
We can use CloudWatch Alarms or Lambda to trigger SNS notifications based on scaling events or health checks.

### 5. Infrastructure Automation Script
End-to-End Automation Script for deployment and teardown of the infrastructure is can be seen here [automation_script](automation_script.py)

