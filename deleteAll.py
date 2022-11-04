import boto3
from botocore.config import Config
from pprint import pprint
import base64


ACCESS_KEY = ""
SECRET_KEY = ""

# 아래와 같이 resource_ids와 resource_arns 값을 넣어줘야 함
resource_ids = {
    'bastion': 'i-0d3f7fe9e839a1ae6',
    'bastion_sg': 'sg-0211acc571f142a5a',
    'db_sg': 'sg-065f7a34184f442f9',
    'internet_gateway': 'igw-0c5d5a070cf31de0c',
    'launch_template_was': 'lt-0170cdf32cff85444',
    'nat_eip_allocation_id': 'eipalloc-0fb4ac5df70b85a41',
    'nat_gateway': 'nat-05564b33c178c3380',
    'route_table_private': 'rtb-0b27b85eefa6cd08e',
    'route_table_private_with_nat': 'rtb-0f65accd4eda5d056',
    'route_table_public': 'rtb-002b848b1328e9a05',
    'subnet_private_db_01': 'subnet-0eab69375596125eb',
    'subnet_private_db_02': 'subnet-012d40e29140c5c27',
    'subnet_private_was_01': 'subnet-018e5de09f7b43708',
    'subnet_private_was_02': 'subnet-0dcd4a174d5776272',
    'subnet_private_was_lb_01': 'subnet-0731b14eb8af7ba79',
    'subnet_private_was_lb_02': 'subnet-0c7b02e40ac176ba6',
    'subnet_private_web_01': 'subnet-09c0faf24522351d8',
    'subnet_private_web_02': 'subnet-099f3733f73d8105f',
    'subnet_public_detault_01': 'subnet-04b3e047b268a50c2',
    'subnet_public_detault_02': 'subnet-0e6f05d52159747b5',
    'subnet_public_web_lb_01': 'subnet-04dc30ab5483138e0',
    'subnet_public_web_lb_02': 'subnet-022c16fb8d693377f',
    'vpc': 'vpc-060b528438f75fcdb',
    'was_lb_sg': 'sg-0ef9402e275d6fcbc',
    'was_sg': 'sg-00865b20e7b09db44',
    'web_lb_sg': 'sg-0635acdf832d2fa2e',
    'web_sg': 'sg-07a4ceced61c21d3e'}
resource_arns = {
    'was_lb': 'arn:aws:elasticloadbalancing:ap-northeast-2:999822656998:loadbalancer/app/wasLB/d87cca9a8006407a',
    'was_lb_tg': 'arn:aws:elasticloadbalancing:ap-northeast-2:999822656998:targetgroup/was-lb-tg/46a96268844302b7',
    'web_lb': 'arn:aws:elasticloadbalancing:ap-northeast-2:999822656998:loadbalancer/app/webLB/d9c43e1dd1131adf',
    'web_lb_tg': 'arn:aws:elasticloadbalancing:ap-northeast-2:999822656998:targetgroup/web-lb-tg/62a23f8d045ed188'}

my_config = Config(
    region_name = 'ap-northeast-2'
)
session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

# Auto Scaling Group 제거(web-asg, was-asg)
asg_client = session.client('autoscaling', config=my_config)
response = asg_client.delete_auto_scaling_group(
    AutoScalingGroupName='was-asg',
    ForceDelete=True,
)
response = asg_client.delete_auto_scaling_group(
    AutoScalingGroupName='web-asg',
    ForceDelete=True,
)

# Launch Template 제거
ec2_client = session.client('ec2', config=my_config)
ec2_client.delete_launch_template(
    LaunchTemplateName='launch-template-was'
)
ec2_client.delete_launch_template(
    LaunchTemplateName='launch-template-web'
)

# Load Balancer 제거(webLB, wasLB)
elb_client = session.client('elbv2', config=my_config)
elb_client.delete_load_balancer(
    LoadBalancerArn=resource_arns['web_lb'],
)
elb_client.delete_load_balancer(
    LoadBalancerArn=resource_arns['was_lb'],
)

# Target Group 제거(web-lb-tg, was-lb-tg)
elb_client = session.client('elbv2', config=my_config)
response = elb_client.delete_target_group(
    TargetGroupArn=resource_arns['web_lb_tg'],
)
response = elb_client.delete_target_group(
    TargetGroupArn=resource_arns['was_lb_tg'],
)

# Bastion host 제거
ec2_client = session.client('ec2', config=my_config)
ec2_client.terminate_instances(
    InstanceIds=[
        resource_ids['bastion'],
    ],
)

# RDS 제거
rds_client = session.client('rds', config=my_config)
response = rds_client.delete_db_instance(
    DBInstanceIdentifier='rdsinstances',
    SkipFinalSnapshot=True,
    DeleteAutomatedBackups=False
)

# Security Group 제거 ID 필요
ec2_client = session.client('ec2', config=my_config)
ec2_client.delete_security_group(
    GroupId=resource_ids['db_sg'], # db_sg
)
ec2_client.delete_security_group(
    GroupId=resource_ids['was_sg'], # was_sg
)
ec2_client.delete_security_group(
    GroupId=resource_ids['was_lb_sg'], # was_lb_sg
)
ec2_client.delete_security_group(
    GroupId=resource_ids['web_sg'], # web_sg
)
ec2_client.delete_security_group(
    GroupId=resource_ids['web_lb_sg'], # web_lb_sg
)
ec2_client.delete_security_group(
    GroupId=resource_ids['bastion_sg'], # bastion_sg
)

# Public Route Table에서 IGW 연결한 Route 제거
ec2_client.delete_route(
    DestinationCidrBlock='0.0.0.0/0',
    RouteTableId=resource_ids['route_table_public']
)

# Route Table 제거
ec2_client.delete_route_table(
    RouteTableId=resource_ids['route_table_private']
)
ec2_client.delete_route_table(
    RouteTableId=resource_ids['route_table_private_with_nat']
)

# NAT Gateway 제거
ec2_client.delete_nat_gateway(
    NatGatewayId=resource_ids['nat_gateway']
)

# NAT Gateway를 위한 EIP 제거 (할당 ID 필요)
ec2_client.release_address(
    AllocationId=resource_ids['nat_eip_allocation_id'],
)

# Internet Gateway를 VPC에서 분리
ec2_client.detach_internet_gateway(
    InternetGatewayId=resource_ids['internet_gateway'],
    VpcId=resource_ids['vpc']
)

# Internet Gateway 제거
ec2_client.delete_internet_gateway(
    InternetGatewayId=resource_ids['internet_gateway']
)

# Subnet 제거
ec2_client = session.client('ec2', config=my_config)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_private_was_lb_02'], # subnet_private_was_lb_02
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_private_was_lb_01'], # subnet_private_was_lb_01
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_public_web_lb_02'], # subnet_public_web_lb_02
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_public_web_lb_01'], # subnet_public_web_lb_01
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_private_db_02'], # subnet_private_db_02
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_private_db_01'], # subnet_private_db_01
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_private_was_02'], # subnet_private_was_02
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_private_was_01'], # subnet_private_was_01
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_private_web_02'], # subnet_private_web_02
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_private_web_01'], # subnet_private_web_01
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_public_detault_02'], # subnet_public_detault_02
)
response = ec2_client.delete_subnet(
    SubnetId=resource_ids['subnet_public_detault_01'], # subnet_public_detault_01
)

# 키 페어 제거
ec2_client.delete_key_pair(
    KeyName='keypair',
)

# VPC 제거
response = ec2_client.delete_vpc(
    VpcId=resource_ids['vpc'],
)

print("자원 제거 완료")