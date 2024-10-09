import boto3
def create_s3_bucket():
  s3 = boto3.client('s3')
  bucket_name = 'ramananda_s3_bucket'
  s3.create_bucket(Bucket=bucket_name)
  # Upload static files
  s3.upload_file('/static_files/sample.txt', 'mybucket', 'sample.txt')

def launch_ec2_instance():
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
    echo "Hello World from $(hostname -f)" > /var/www/html/index.html''')
    instance_id = instance[0].id
    print(instance_id)

    
def create_load_balancer():
  elb = boto3.client('elbv2')
  load_balancer = elb.create_load_balancer(
    Name='ramananda-lb',
    Subnets=['subnet-03ca36de9a927fe8e', 'subnet-09bd0e0acc92d4efa'], 
    SecurityGroups=['sg-057f0e6c8849c7ff8 (default)'])
  lb_arn = load_balancer['LoadBalancers'][0]['LoadBalancerArn']
  elb.register_targets(
    TargetGroupArn='HTML-Prashant-b7-1',
    Targets=[{'Id': instance_id, 'Port': 80}],
    VpcId='vpc-0321f38a7b594180d'
  )
    
def configure_auto_scaling():
    autoscaling = boto3.client('autoscaling')
    response = autoscaling.create_launch_configuration(
    LaunchConfigurationName='web-app-launch-config',
    ImageId='ami-0e42b3cc568cd07e3',
    InstanceType='t4g.micro',
    KeyName='ramananda_key',
    SecurityGroups=['sg-057f0e6c8849c7ff8'])

    response = autoscaling.create_auto_scaling_group(
    AutoScalingGroupName='web-app-asg',
    LaunchConfigurationName='web-app-launch-config',
    MinSize=1,
    MaxSize=5,
    DesiredCapacity=2,
    VPCZoneIdentifier='subnet-0123456789abcdef0,subnet-0123456789abcdef1',
    TargetGroupARNs=['your-target-group-arn'],)

    cloudwatch = boto3.client('cloudwatch')
    scaling_policy = autoscaling.put_scaling_policy(
    AutoScalingGroupName='web-app-asg',
    PolicyName='ScaleOutPolicy',
    AdjustmentType='ChangeInCapacity',
    ScalingAdjustment=1,
    Cooldown=300)
  
def set_up_sns_notifications():
    sns = boto3.client('sns')
    response = sns.create_topic(Name='scaling-alerts')
    topic_arn = response['TopicArn']
    response = sns.subscribe(
    TopicArn=topic_arn,
    Protocol='email',
    Endpoint='ramhnaik@gmail.com')

def terminate_ec2_instance(instance_id, region='us-west-2'):
    ec2 = boto3.resource('ec2', region_name=region)
    instance = ec2.Instance(instance_id)
    
    response = instance.terminate()
    instance.wait_until_terminated()
    
    print(f"EC2 instance {instance_id} terminated.")


def delete_auto_scaling_group(asg_name, region='us-west-2):
    asg = boto3.client('autoscaling', region_name=region)
    
    response = asg.update_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        MinSize=0,
        MaxSize=0,
        DesiredCapacity=0
    )
    
    asg.delete_auto_scaling_group(AutoScalingGroupName=asg_name, ForceDelete=True)
    print(f"Auto Scaling Group {asg_name} deleted.")


def delete_load_balancer(lb_arn, region='us-west-2'):
    elb = boto3.client('elbv2', region_name=region)
    response = elb.delete_load_balancer(LoadBalancerArn=lb_arn)
    print(f"Load Balancer {lb_arn} deleted.")


def delete_target_group(tg_arn, region='us-west-2'):
    elb = boto3.client('elbv2', region_name=region)
    response = elb.delete_target_group(TargetGroupArn=tg_arn)
    print(f"Target Group {tg_arn} deleted.")


def delete_s3_bucket(bucket_name, region='us-west-2'):
    s3 = boto3.resource('s3', region_name=region)
    bucket = s3.Bucket(bucket_name) 
    # Delete all objects from the bucket
    bucket.objects.delete()    
    # Delete the bucket itself
    bucket.delete()
    print(f"S3 bucket {bucket_name} deleted.")


def delete_sns_topic(topic_arn, region='us-west-2'):
    sns = boto3.client('sns', region_name=region) 
    response = sns.delete_topic(TopicArn=topic_arn)
    print(f"SNS topic {topic_arn} deleted.")


def delete_cloudwatch_alarm(alarm_name, region='us-west-2'):
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    response = cloudwatch.delete_alarms(AlarmNames=[alarm_name])
    print(f"CloudWatch Alarm {alarm_name} deleted.")


def deploy_infrastructure():
    create_s3_bucket()
    launch_ec2_instance()
    create_load_balancer()
    configure_auto_scaling()
    set_up_sns_notifications()

def teardown_infrastructure(instance_id, asg_name, lb_arn, tg_arn, bucket_name, sns_topic_arn, alarm_name, region='us-east-1'):
 
    terminate_ec2_instance(instance_id, region)
    delete_auto_scaling_group(asg_name, region)
    delete_load_balancer(lb_arn, region)
    delete_target_group(tg_arn, region)
    delete_s3_bucket(bucket_name, region)
    delete_sns_topic(sns_topic_arn, region)
    delete_cloudwatch_alarm(alarm_name, region)
    
    print("All infrastructure components have been successfully deleted.")



if __name__ == "__main__":
    instance_id = 'i-09b80b8950cc83497'
    asg_name = 'my-asg'
    lb_arn = 'ramananda-lb'
    tg_arn = 'HTML-Prashant-b7-1'
    bucket_name = 'ramananda_s3_bucket'
    sns_topic_arn = 'scaling-alerts-ramananda'
    alarm_name = 'AutoScalingAlarm_Ramananda'
    deploy_infrastructure()
    # teardown_infrastructure(instance_id, asg_name, lb_arn, tg_arn, bucket_name, sns_topic_arn, alarm_name)
