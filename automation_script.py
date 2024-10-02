def create_s3_bucket()
  import boto3
  s3 = boto3.client('s3')
  bucket_name = 'ramananda_s3_bucket'
  s3.create_bucket(Bucket=bucket_name)
  # Upload static files
  s3.upload_file('/static_files/sample.txt', 'mybucket', 'sample.txt')

def launch_ec2_instance()
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
    echo "Hello World from $(hostname -f)" > /var/www/html/index.html''')
    instance_id = instance[0].id
    print(instance_id)

    
def create_load_balancer()
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
    
def configure_auto_scaling()
  
def set_up_sns_notifications()

def delete_auto_scaling_group()
    
def terminate_ec2_instances()
    
def delete_s3_bucket()


def deploy_infrastructure():
    create_s3_bucket()
    launch_ec2_instance()
    create_load_balancer()
    configure_auto_scaling()
    set_up_sns_notifications()

def teardown_infrastructure():
    delete_auto_scaling_group()
    terminate_ec2_instances()
    delete_s3_bucket()

if __name__ == "__main__":
    deploy_infrastructure()
    # teardown_infrastructure()
