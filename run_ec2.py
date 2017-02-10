import os
import sys
import time
import boto.ec2

ec2conn = boto.ec2.connect_to_region(os.environ['AWS_REGION'], aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_KEY'])


def run_ec2():

 ec2conn.run_instances(
   os.environ['AMI_ID'],
   subnet_id = os.environ['SUBNET_ID'],
   key_name = os.environ['KEY'],
   instance_type=os.environ['INSTANCE_TYPE'],
   security_group_ids = [os.environ['SG_ID']]
 )

 sys.stdout.write('Getting IP address')
 sys.stdout.flush()
 for i in range(1,30):
  sys.stdout.write('.')
  sys.stdout.flush()
  time.sleep(1)
  if ec2conn.get_all_instance_status():
   print '.'
   break

 print '.'

 if ec2conn.get_all_instance_status():
  print "Instance is ready"
 else:
  print "Instance never got ready"
  quit()
 
 return


## Run EC2 instance

if ec2conn.get_all_instance_status():
 print('OpenVPN Server is already running...')
else:
 print('Start OpenVPN Server...')
 run_ec2()


# Export OpenVPN Server IP addresses

ec2_id = ec2conn.get_all_instance_status()[0].id
os.putenv('PUBLIC_DNS_NAME',ec2conn.get_all_instances(instance_ids=[ec2_id])[0].instances[0].public_dns_name)
os.putenv('PRIVATE_IP_ADDRESS',ec2conn.get_all_instances(instance_ids=[ec2_id])[0].instances[0].private_ip_address)
os.system('bash')

