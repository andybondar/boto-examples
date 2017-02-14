import os
import sys
import time
import boto.ec2
import socket
import fcntl
import struct
import re
import subprocess

ec2conn = boto.ec2.connect_to_region(os.environ['AWS_REGION'], aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_KEY'])

### Define functions

def run_ec2():

 ec2conn.run_instances(
   os.environ['AMI_ID'],
   subnet_id = os.environ['SUBNET_ID'],
   key_name = os.environ['KEY'],
   instance_type=os.environ['INSTANCE_TYPE'],
   security_group_ids = [os.environ['SG_ID']]
 )

 print 'Getting EC2 instance status'
 for i in range(1,60):
  time.sleep(1)
  if ec2conn.get_all_instance_status():
   break

 if ec2conn.get_all_instance_status():
  print "Instance is ready"
  return True
 else:
  print "Instance isn't ready"
  return False


def check_port(port):
 s = socket.socket()
 print "Attempting to connect to %s on port %s" % (public_name, port)
 try:
  s.connect((public_name, port))
  print "Connected to %s on port %s" % (public_name, port)
  return True
 except socket.error, e:
  print "Connection to %s on port %s failed: %s" % (public_name, port, e)
  return False

def get_ip_address(ifname):
 s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 return socket.inet_ntoa(fcntl.ioctl(
   s.fileno(),
   0x8915,
   struct.pack('256s', ifname[:15])
 )[20:24])


### 

## Run EC2 instance

if ec2conn.get_all_instance_status():
 print('OpenVPN Server is already running...')
else:
 print('Start OpenVPN Server...')
 ec2_result = run_ec2()
 if ec2_result:
  print('OpenVPN Server is running')
 else:
  print('OpenVPN Server failed to start for some reason')
  exit(1)


# Get OpenVPN Server IP addresses

ec2_id = ec2conn.get_all_instance_status()[0].id
public_name = ec2conn.get_all_instances(instance_ids=[ec2_id])[0].instances[0].public_dns_name
private_ip = ec2conn.get_all_instances(instance_ids=[ec2_id])[0].instances[0].private_ip_address

print "FQDN: " + public_name
print "Private IP: " + private_ip

# Check that port 443 is available

as_result = check_port(port=443)
if as_result:
 print('OpenVPN Server is accessible')
else:
 print('OpenVPN Server is not accessible')
 exit(1)

print "Create new client.ovpn file"
input = open("client.ovpn.origin","r")
output = open("client.ovpn","w")
for line in input:
 output.write(re.sub('openvpnas_hostname', public_name, line))

input.close()
output.close()

print "Run VPN client"
subprocess.call(["sudo killall openvpn"], shell=True)
subprocess.call(["sudo openvpn --config client.ovpn --daemon"], shell=True)
time.sleep(10)

print "Verify VPN connection"
vpn = subprocess.call(["ip addr list tun0"], shell=True)
if vpn == 1:
 print('VPN connection failed')
 exit(1)
else:
 print('VPN connection successfully established')

print "Create file containing SonarQube server IP"
sonarqube_ip = get_ip_address('tun0')
file = open("sonarqube_ip","w")
file.write("SONARQUBE_IP=" + sonarqube_ip)
file.close()


