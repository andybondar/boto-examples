import os
import sys
import time
import boto.ec2

service_port=2022

ec2conn = boto.ec2.connect_to_region(os.environ['AWS_REGION'], aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_KEY'])


def run_ec2():

 ec2conn.run_instances(
   os.environ['AMI_ID'],
   subnet_id = os.environ['SUBNET_ID'],
   key_name = os.environ['KEY'],
   instance_type=os.environ['INSTANCE_TYPE'],
   security_group_ids = [os.environ['SG_ID']]
 )

 sys.stdout.write('Getting EC2 instance status')
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

def check_port(hostname,port):
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 result = sock.connect_ex((hostname,port))
 return result


## Run EC2 instance

if ec2conn.get_all_instance_status():
 print('OpenVPN Server is already running...')
else:
 print('Start OpenVPN Server...')
 run_ec2()


# Get OpenVPN Server IP addresses

ec2_id = ec2conn.get_all_instance_status()[0].id
public_name = ec2conn.get_all_instances(instance_ids=[ec2_id])[0].instances[0].public_dns_name
private_ip = ec2conn.get_all_instances(instance_ids=[ec2_id])[0].instances[0].private_ip_address

print "FQDN: " + public_name
print "Private IP: " + private_ip

