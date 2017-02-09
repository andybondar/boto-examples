import os
import boto.ec2

ec2conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_KEY'])

# Run EC2 instance

ec2conn.run_instances(
	'ami-acb87fba',
	subnet_id='subnet-489a9e01',
	key_name='sonarqube',
        instance_type='t2.small',
        security_group_ids=['sg-ee355692'])

print ec2conn.get_all_instances()

