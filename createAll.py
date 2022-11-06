import boto3
from botocore.config import Config
from pprint import pprint
import base64
import time

ACCESS_KEY = ""
SECRET_KEY = ""

resource_ids={}
resource_arns={}

my_config = Config(
    region_name = 'ap-northeast-2'
)
session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

ec2_resource = session.resource('ec2', config=my_config)
ec2_client = session.client('ec2', config=my_config)


## DB 서브넷 생성
subnet_private_db_01 = vpc.create_subnet(AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.6.0/24')
response = ec2_client.create_tags(Resources=[subnet_private_db_01.id,],Tags=[{'Key': 'Name','Value': 'subnet_private_db_01',},],)
resource_ids['subnet_private_db_01'] = subnet_private_db_01.id
subnet_private_db_02 = vpc.create_subnet(AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.7.0/24')
response = ec2_client.create_tags(Resources=[subnet_private_db_02.id,],Tags=[{'Key': 'Name','Value': 'subnet_private_db_02',},],)
resource_ids['subnet_private_db_02'] = subnet_private_db_02.id
### Private 라우트 테이블 생성
route_table_private = ec2_resource.create_route_table(VpcId=resource_ids['vpc'],)
resource_ids['route_table_private'] = route_table_private.id
# Private 라우트 테이블을 DB subnet에 연결
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_private'],
    SubnetId=resource_ids['subnet_private_db_01'],
)
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_private'],
    SubnetId=resource_ids['subnet_private_db_02'],
)

## WEB_LB Subnet 생성
subnet_public_web_lb_01 = vpc.create_subnet(AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.8.0/24')
response = ec2_client.create_tags(Resources=[subnet_public_web_lb_01.id,],Tags=[{'Key': 'Name','Value': 'subnet_public_web_lb_01',},],)
resource_ids['subnet_public_web_lb_01'] = subnet_public_web_lb_01.id
subnet_public_web_lb_02 = vpc.create_subnet(AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.9.0/24')
response = ec2_client.create_tags(Resources=[subnet_public_web_lb_02.id,],Tags=[{'Key': 'Name','Value': 'subnet_public_web_lb_02',},],)
resource_ids['subnet_public_web_lb_02'] = subnet_public_web_lb_02.id
### Internet gateway가 연결되어 있는 Public 라우드 테이블을 WEB LB subnet에 연결
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_public'],
    SubnetId=resource_ids['subnet_public_web_lb_01'],
)
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_public'],
    SubnetId=resource_ids['subnet_public_web_lb_02'],
)

## WEB Subnet 생성
subnet_private_web_01 = vpc.create_subnet(AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.2.0/24')
response = ec2_client.create_tags(Resources=[subnet_private_web_01.id,],Tags=[{'Key': 'Name','Value': 'subnet_private_web_01',},],)
resource_ids['subnet_private_web_01'] = subnet_private_web_01.id
subnet_private_web_02 = vpc.create_subnet(AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.3.0/24')
response = ec2_client.create_tags(Resources=[subnet_private_web_02.id,],Tags=[{'Key': 'Name','Value': 'subnet_private_web_02',},],)
resource_ids['subnet_private_web_02'] = subnet_private_web_02.id

### 생성한 Private with NAT 라우트 테이블을 WEB 서브넷에 연결
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_private_with_nat'],
    SubnetId=resource_ids['subnet_private_web_01'],
)
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_private_with_nat'],
    SubnetId=resource_ids['subnet_private_web_02'],
)

## WAS LB Subnet 생성
subnet_private_was_lb_01 = vpc.create_subnet(AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.10.0/24')
response = ec2_client.create_tags(Resources=[subnet_private_was_lb_01.id,],Tags=[{'Key': 'Name','Value': 'subnet_private_was_lb_01',},],)
resource_ids['subnet_private_was_lb_01'] = subnet_private_was_lb_01.id
subnet_private_was_lb_02 = vpc.create_subnet(AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.11.0/24')
response = ec2_client.create_tags(Resources=[subnet_private_was_lb_02.id,],Tags=[{'Key': 'Name','Value': 'subnet_private_was_lb_02',},],)
resource_ids['subnet_private_was_lb_02'] = subnet_private_was_lb_02.id
### Private 라우트 테이블을 WAS LB 서브넷에 연결
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_private'],
    SubnetId=resource_ids['subnet_private_was_lb_01'],
)
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_private'],
    SubnetId=resource_ids['subnet_private_was_lb_02'],
)

## WAS Subnet 생성
subnet_private_was_01 = vpc.create_subnet(AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.4.0/24')
response = ec2_client.create_tags(Resources=[subnet_private_was_01.id,],Tags=[{'Key': 'Name','Value': 'subnet_private_was_01',},],)
resource_ids['subnet_private_was_01'] = subnet_private_was_01.id
subnet_private_was_02 = vpc.create_subnet(AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.5.0/24')
response = ec2_client.create_tags(Resources=[subnet_private_was_02.id,],Tags=[{'Key': 'Name','Value': 'subnet_private_was_02',},],)
resource_ids['subnet_private_was_02'] = subnet_private_was_02.id

### Private with NAT 라우트 테이블을 WAS 서브넷에 연결
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_private_with_nat'],
    SubnetId=resource_ids['subnet_private_was_01'],
)
response = ec2_client.associate_route_table(
    RouteTableId=resource_ids['route_table_private_with_nat'],
    SubnetId=resource_ids['subnet_private_was_02'],
)
# Subnet 생성 완료

# 보안 그룹 생성
## Bastion 보안 그룹 생성
bastion_sg = ec2_resource.create_security_group(
    Description='bastion_sg',
    GroupName='bastion_sg',
    VpcId=resource_ids['vpc']
)
resource_ids['bastion_sg']=bastion_sg.id
response = bastion_sg.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 22,
            'IpProtocol': 'tcp',
            'ToPort': 22,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Accept ssh connection from all'
                },
            ],
        },
    ],
)
## WEB LB 보안 그룹 생성
web_lb_sg = ec2_resource.create_security_group(
    Description='web_lb_sg',
    GroupName='web_lb_sg',
    VpcId=resource_ids['vpc']
)
resource_ids['web_lb_sg']=web_lb_sg.id
response = web_lb_sg.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 80,
            'IpProtocol': 'tcp',
            'ToPort': 80,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Accept HTTP from ALL'
                },
            ],
        },
        {
            'FromPort': 443,
            'IpProtocol': 'tcp',
            'ToPort': 443,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Accept HTTPS from ALL'
                },
            ],
        },
    ],
)
## WEB 보안 그룹 생성
web_sg = ec2_resource.create_security_group(
    Description='web_sg',
    GroupName='web_sg',
    VpcId=resource_ids['vpc']
)
resource_ids['web_sg']=web_sg.id
response = web_sg.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 22,
            'IpProtocol': 'tcp',
            'ToPort': 22,
            "UserIdGroupPairs": [{'GroupId': resource_ids['bastion_sg'], 'Description': 'Accept ssh connection from bastion'},]
        },
        {
            'FromPort': 80,
            'IpProtocol': 'tcp',
            'ToPort': 80,
            "UserIdGroupPairs": [{'GroupId': resource_ids['web_lb_sg'], 'Description': 'Accept HTTP connection from WEB LB'},]
        },
    ],
)
## WAS LB 보안 그룹 생성
was_lb_sg = ec2_resource.create_security_group(
    Description='was_lb_sg',
    GroupName='was_lb_sg',
    VpcId=resource_ids['vpc']
)
resource_ids['was_lb_sg']=was_lb_sg.id
response = was_lb_sg.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 8080,
            'IpProtocol': 'tcp',
            'ToPort': 8080,
            "UserIdGroupPairs": [{'GroupId': resource_ids['web_sg'], 'Description': 'Accept HTTP from web'}]
        },
    ],
)
## WAS 보안 그룹 생성
was_sg = ec2_resource.create_security_group(
    Description='was_sg',
    GroupName='was_sg',
    VpcId=resource_ids['vpc']
)
resource_ids['was_sg']=was_sg.id
response = was_sg.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 22,
            'IpProtocol': 'tcp',
            'ToPort': 22,
            "UserIdGroupPairs": [{'GroupId': resource_ids['bastion_sg'], 'Description': 'Accept SSH from bastion'}]
        },
        {
            'FromPort': 8080,
            'IpProtocol': 'tcp',
            'ToPort': 8080,
            "UserIdGroupPairs": [
                {'GroupId': resource_ids['was_lb_sg'], 'Description': 'Accept HTTP from was_lb'}
            ]
        },
    ],
)
## DB(RDS) 보안 그룹 생성
db_sg = ec2_resource.create_security_group(
    Description='db_sg',
    GroupName='db_sg',
    VpcId=resource_ids['vpc']
)
resource_ids['db_sg']=db_sg.id
response = db_sg.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 3306,
            'IpProtocol': 'tcp',
            'ToPort': 3306,
            "UserIdGroupPairs": [{'GroupId': resource_ids['was_sg'], 'Description': 'Accept HTTP from web'}]
        },
    ],
)
# 보안 그룹 생성 완료

# DB 생성
## DB 서브넷 그룹 생성
rds_client = session.client('rds', config=my_config)
response = rds_client.create_db_subnet_group(
    DBSubnetGroupName='db_subnet_group',
    DBSubnetGroupDescription='db_subnet_group',
    SubnetIds=[
        resource_ids['subnet_private_db_01'],
        resource_ids['subnet_private_db_02']
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': 'db_subnet_group'
        },
    ]
)
## DB 인스턴스 생성
rds_client = session.client('rds', config=my_config)
rds_instances = rds_client.create_db_instance(
    DBName='rds',
    DBInstanceIdentifier= 'rdsInstances',
    AllocatedStorage=10,
    DBInstanceClass='db.t2.micro', # DB 인스턴스 사양
    Engine='mariadb', # DB 엔진
    MasterUsername='root', # master user name
    MasterUserPassword='password', # master user password
    VpcSecurityGroupIds=[
        resource_ids['db_sg'],
    ],
    # AvailabilityZone='ap-northeast-2a', Multi AZ 옵션일 때는 AZ 지정 불가
    DBSubnetGroupName='db_subnet_group', # DB 서브넷 그룹 지정
    Port=3306, # DB Port
    MultiAZ=True, # 다중 AZ 구성
    EngineVersion='10.3.36', # Engine Version
    PubliclyAccessible=False, # 외부 접속 여부
    Tags=[
        {
            'Key': 'Name',
            'Value': 'mariadb'
        },
    ],
)

### 생성된 DB의 Endpoint가 이후 과정에서 필요한데, Endpoint가 생성되는데 시간이 오래 걸림
print ("Sleep 5 minute from now on...")
print("생성된 DB의 Endpoint가 이후 과정에서 필요한데, Endpoint가 생성되는데 시간이 오래 걸림")
time.sleep(300)
print("wake up!")

rds_instances = rds_client.describe_db_instances(DBInstanceIdentifier='rdsInstances')
RDS_ENDPOINT = rds_instances['DBInstances'][0].get('Endpoint').get('Address')
print("RDS Endpoint =", RDS_ENDPOINT)
# DB 생성 완료

# WAS 생성(LB, Target Group, Launch Template, ASG)
## WAS LB 생성
elb_client = session.client('elbv2', config=my_config)
was_lb = elb_client.create_load_balancer(
    Name='wasLB',
    Subnets=[
        resource_ids['subnet_private_was_lb_01'],
        resource_ids['subnet_private_was_lb_02'],
    ],
    SecurityGroups=[
        resource_ids['was_lb_sg'],
    ],
    Scheme='internal',
    Type='application',
    IpAddressType='ipv4',
)
resource_arns['was_lb'] = was_lb['LoadBalancers'][0]['LoadBalancerArn']
WAS_LB_ENDPOINT = was_lb['LoadBalancers'][0]['DNSName']
## WAS LB Target Group 생성
was_lb_tg = elb_client.create_target_group(
    Name='was-lb-tg',
    Protocol='HTTP',
    ProtocolVersion='HTTP1',
    Port=8080,
    VpcId=resource_ids['vpc'],
    HealthCheckProtocol='HTTP',
    HealthCheckPort='8080',
    HealthCheckEnabled=True,
    HealthCheckPath='/',
    HealthCheckIntervalSeconds=10,
    HealthCheckTimeoutSeconds=6,
    HealthyThresholdCount=2,
    UnhealthyThresholdCount=2,
    Matcher={
        'HttpCode': "200-499", # 편의상 넓게 지정함
    },
    TargetType='instance',
    IpAddressType='ipv4'
)
resource_arns['was_lb_tg'] = was_lb_tg['TargetGroups'][0]['TargetGroupArn']
## WAS LB 리스너 생성
was_lb_listener = elb_client.create_listener(
    LoadBalancerArn=resource_arns['was_lb'],
    Protocol='HTTP',
    Port=8080,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': resource_arns['was_lb_tg'],
        },
    ],
)
## WAS 생성
### WAS Initial Script
user_data_was = f'''
#!/bin/bash
sudo yum install java-1.8.0-openjdk.x86_64 -y
sudo yum install java-1.8.0-openjdk-devel.x86_64 -y
wget https://dlcdn.apache.org/tomcat/tomcat-8/v8.5.83/bin/apache-tomcat-8.5.83.tar.gz
sudo tar xvfz apache-tomcat-8.5.83.tar.gz
sudo mv apache-tomcat-8.5.83 /usr/local/tomcat8.5

cat <<EOF > /etc/profile.d/tomcat.sh
export JAVA_HOME=$(echo $(readlink -f $(which javac)) | cut -d '/' -f 1,2,3,4,5)
export CATALINA_HOME=/usr/local/tomcat8.5
export CLASSPATH=.:\$JAVA_HOME/jre/lib/ext:$JAVA_HOME/lib/tools.jar:\$CATALINA_HOME/lib/jsp-api.jar:\$CATALINA_HOME/lib/servlet-api.jar
export JDK_HOME=\$JAVA_HOME
export PATH=\$PATH:\$JAVA_HOME/bin:\$CATALINA_HOME/bin
EOF

mkdir /usr/local/tomcat8.5/webapps/ROOT/WEB-INF/lib
wget https://dlm.mariadb.com/2338663/Connectors/java/connector-java-2.7.6/mariadb-java-client-2.7.6.jar /usr/local/tomcat8.5/webapps/ROOT/WEB-INF/lib

cat<<EOF > /usr/local/tomcat8.5/webapps/ROOT/db-user.jsp
<%@page import="java.sql.SQLException"%>
<%@page import="java.sql.ResultSet"%>
<%@page import="java.sql.Statement"%>
<%@page import="java.sql.Connection"%>
<%@page import="java.sql.DriverManager"%>
<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<title>MySQL 유저 목록</title>
</head>
<body>
mysql.user 테이블의 내용<br>
<table width="100%;" border="1">
        <tr>
                <th>Host</th><th>User</th>
        </tr>
<%
//1. JDBC 드라이버 로딩
Connection conn = null;
Statement stmt = null;
ResultSet rs = null;
try{{
    //2. 데이터베이스 커넥션(연결객체) 생성
    //1) jdbcDriver? 2) 계정아이디? 3) 비밀번호?
    String url = "jdbc:mariadb://{RDS_ENDPOINT}:3306/mysql";
    String user = "root";
    String password1 = "password";
    Class.forName("org.mariadb.jdbc.Driver");

    String query = "SELECT Host, User FROM user";
    conn = DriverManager.getConnection(url, user, password1);
    //3. Statement 생성
    stmt = conn.createStatement();
    //4. 쿼리 실행
    rs = stmt.executeQuery(query);
    //5. 쿼리 실행 결과 화면 출력
    while(rs.next()){{
            out.print("<tr>");
            out.print("<td>" + rs.getString("Host") + "</td>");
            out.print("<td>" + rs.getString("User") + "</td>");
            out.print("</tr>");
    }}
}}catch(SQLException ex){{
    out.print(ex.getMessage());
    ex.printStackTrace();
}}finally{{
    //6. 사용한 Statement 객체 종료
    if(rs!=null)try{{rs.close();}}catch(SQLException ex){{}}
    if(stmt!=null)try{{stmt.close();}}catch(SQLException ex){{}}
    //7. 커넥션 객체 종료
    if(conn!=null)try{{conn.close();}}catch(SQLException ex){{}}
}}
%>
</table>
</body>
</html>
EOF

source /etc/profile
export RDS_ENDPOINT={RDS_ENDPOINT}
cd $CATALINA_HOME
./bin/startup.sh
'''
user_data_bytes_was = user_data_was.encode('ascii')
base64_bytes_was = base64.b64encode(user_data_bytes_was)
base64_user_data_was = base64_bytes_was.decode('ascii')
### 위에서 base64로 인코딩한 Initial Script를 추가하여 Launch Template 생성
launch_template_was = ec2_client.create_launch_template(
    LaunchTemplateName='launch-template-was',
    LaunchTemplateData={
        'ImageId': 'ami-07810a490b4267374', # Amazon Linux 2
        'InstanceType': 't2.micro',
        'KeyName': 'keypair',
        'UserData': base64_user_data_was,
        'SecurityGroupIds': [
            resource_ids['was_sg'],
        ],
    },
)
resource_ids['launch_template_was'] = launch_template_was['LaunchTemplate']['LaunchTemplateId']
# WAS Auto Scaling Group 생성
asg_client = session.client('autoscaling', config=my_config)
asg_was = asg_client.create_auto_scaling_group(
    AutoScalingGroupName='asg-was',
    LaunchTemplate={
        'LaunchTemplateName': 'launch-template-was',
        'Version': '$Latest'
    },
    MinSize=2,
    MaxSize=4,
    DesiredCapacity=2,
    TargetGroupARNs=[
        resource_arns['was_lb_tg'],
    ],
    VPCZoneIdentifier=resource_ids['subnet_private_was_01']+','+resource_ids['subnet_private_was_02'],
)
### WAS ASG Scaling Policy 추가
response = asg_client.put_scaling_policy(
    AutoScalingGroupName='asg-was',
    PolicyName='cpu-50',
    PolicyType='TargetTrackingScaling',
    TargetTrackingConfiguration={
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'ASGAverageCPUUtilization',
        },
        'TargetValue': 50,
        'DisableScaleIn': False
    },
    Enabled=True,
)
# WAS 생성 완료

# WEB 생성
## WEB LB 생성
elb_client = session.client('elbv2', config=my_config)
web_lb = elb_client.create_load_balancer(
    Name='webLB',
    Subnets=[
        resource_ids['subnet_public_web_lb_01'],
        resource_ids['subnet_public_web_lb_02'],
    ],
    SecurityGroups=[
        resource_ids['web_lb_sg'],
    ],
    Scheme='internet-facing',
    Type='application',
    IpAddressType='ipv4',
)
resource_arns['web_lb'] = web_lb['LoadBalancers'][0]['LoadBalancerArn']
WEB_LB_ENDPOINT = web_lb['LoadBalancers'][0]['DNSName']
## WEB LB Target Group 생성
web_lb_tg = elb_client.create_target_group(
    Name='web-lb-tg',
    Protocol='HTTP',
    ProtocolVersion='HTTP1',
    Port=80,
    VpcId=resource_ids['vpc'],
    HealthCheckProtocol='HTTP',
    HealthCheckPort='80',
    HealthCheckEnabled=True,
    HealthCheckPath='/',
    HealthCheckIntervalSeconds=10,
    HealthCheckTimeoutSeconds=6,
    HealthyThresholdCount=2,
    UnhealthyThresholdCount=2,
    Matcher={
        'HttpCode': "200-499",
    },
    TargetType='instance',
    IpAddressType='ipv4'
)
resource_arns['web_lb_tg'] = web_lb_tg['TargetGroups'][0]['TargetGroupArn']
## WEB LB 리스너 생성
web_lb_listener = elb_client.create_listener(
    LoadBalancerArn=resource_arns['web_lb'],
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': resource_arns['web_lb_tg'],
        },
    ],
)
# web_lb_listener = elb_client.create_listener(
#     LoadBalancerArn=resource_arns['web_lb'],
#     Protocol='HTTPS',
#     Port=443,
#     DefaultActions=[
#         {
#             'Type': 'forward',
#             'TargetGroupArn': resource_arns['web_lb_tg'],
#         },
#     ],
# )
## WEB 생성
### WEB Initial Script 생성
user_data_web = f'''
#!/bin/bash
echo 'test web' > /tmp/hello
sudo yum update -y
sudo yum install -y httpd
sudo systemctl start httpd
sudo systemctl enable httpd
sudo usermod -a -G apache ec2-user
sudo chown -R ec2-user:apache /var/www

cat <<EOF >> /etc/httpd/conf/httpd.conf
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so

<VirtualHost *:80>                                                                                                                          
    ServerName test.com
    ProxyRequests Off                                                                                                                         
    ProxyPreserveHost On                                                                                                                      
    ProxyPass / http://{WAS_LB_ENDPOINT}:8080/
    ProxyPassReverse / http://{WAS_LB_ENDPOINT}:8080/
</VirtualHost>
EOF

systemctl restart httpd
'''
user_data_bytes_web = user_data_web.encode('ascii')
base64_bytes_web = base64.b64encode(user_data_bytes_web)
base64_user_data_web = base64_bytes_web.decode('ascii')
### WEB Launch Template 생성
launch_template_web = ec2_client.create_launch_template(
    LaunchTemplateName='launch-template-web',
    # VersionDescription='1.0',
    LaunchTemplateData={
        'ImageId': 'ami-07810a490b4267374', # Amazon Linux 2
        'InstanceType': 't2.micro',
        'KeyName': 'keypair',
        'UserData': base64_user_data_web,
        'SecurityGroupIds': [
            resource_ids['web_sg'],
        ],
    },
)
### WEB Auto Scaling Group 생성
asg_client = session.client('autoscaling', config=my_config)
asg_web = asg_client.create_auto_scaling_group(
    AutoScalingGroupName='asg-web',
    LaunchTemplate={
        'LaunchTemplateName': 'launch-template-web',
        'Version': '$Latest'
    },
    MinSize=2,
    MaxSize=4,
    DesiredCapacity=2,
    TargetGroupARNs=[
        resource_arns['web_lb_tg'],
    ],
    VPCZoneIdentifier=resource_ids['subnet_private_web_01']+','+resource_ids['subnet_private_web_02'],
)
### WEB ASG Scaling Policy 추가
response = asg_client.put_scaling_policy(
    AutoScalingGroupName='asg-web',
    PolicyName='cpu-50',
    PolicyType='TargetTrackingScaling',
    TargetTrackingConfiguration={
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'ASGAverageCPUUtilization',
        },
        'TargetValue': 50,
        'DisableScaleIn': False
    },
    Enabled=True,
)
# WEB 생성 완료

# Bastion Host 생성
instance = ec2_resource.create_instances(
    ImageId='ami-07810a490b4267374',
    InstanceType='t2.micro',
    KeyName='keypair',
    MaxCount=1,
    MinCount=1,
    # UserData를 실행하는 계정은 root
    UserData=''' 
        #!/bin/bash
        echo "$(whoami)" >> /tmp/hello 
        ''',
    PrivateDnsNameOptions={
        'HostnameType': 'resource-name',
        'EnableResourceNameDnsARecord': True,
    },
    NetworkInterfaces=[
        {
            'AssociatePublicIpAddress': True, # Public IP 부여
            'DeleteOnTermination': True, # 인스턴스 삭제 시 Public IP 반납
            'Description': 'Network Interface for Bastion host',
            'DeviceIndex': 0,
            'Groups': [
                resource_ids['bastion_sg'],
            ],
            'SubnetId': resource_ids['subnet_public_detault_01'],
        },
    ],
)
resource_ids['bastion'] = instance[0].id
# Bastion Host 생성 완료

print("resource_ids=", end=' ')
pprint(resource_ids)
print("resource_arns=", end=' ')
pprint(resource_arns)

print("3-Tier 구성 완료")
print("Endpoint =", WEB_LB_ENDPOINT)


# 아래는 Boto3로 Route53 도메인을 구매하는 코드입니다.
# botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "https://route53domains.aws-global.amazonaws.com/" 와 같은 에러가 발생하는 것으로 보아 현재는 지원되지 않는 것 같습니다.
# 부득이하게 DNS는 수동으로 등록하였습니다.
'''
# Route 53에서 DNS 등록
route53domains_client = session.client('route53domains', config=global_config)
response = route53domains_client.register_domain(
    DomainName='threetier.link',
    DurationInYears=1,
    AutoRenew=False,
    AdminContact={
        'FirstName': 'DongJae',
        'LastName': 'Lee',
        'ContactType': 'PERSON',
        'AddressLine1': 'gyeonginro',
        'State': 'Bucheon-si',
        'CountryCode': 'KR',
        'ZipCode': '14723',
        'PhoneNumber': '821047490943',
        'Email': 'dongjae4@naver.com',
    },
    RegistrantContact={
        'FirstName': 'DongJae',
        'LastName': 'Lee',
        'ContactType': 'PERSON',
        'AddressLine1': 'gyeonginro',
        'State': 'Bucheon-si',
        'CountryCode': 'KR',
        'ZipCode': '14723',
        'PhoneNumber': '821047490943',
        'Email': 'dongjae4@naver.com',
    },
    TechContact={
        'FirstName': 'DongJae',
        'LastName': 'Lee',
        'ContactType': 'PERSON',
        'AddressLine1': 'gyeonginro',
        'State': 'Bucheon-si',
        'CountryCode': 'KR',
        'ZipCode': '14723',
        'PhoneNumber': '821047490943',
        'Email': 'dongjae4@naver.com',
    },
    PrivacyProtectAdminContact=True,
    PrivacyProtectRegistrantContact=True,
    PrivacyProtectTechContact=True
)
'''
# 수동으로 등록해야 하는 것들이 많아 주석처리해놓았습니다. 실제 생성은 코드로 한 것이 맞습니다.
'''
acm_client = session.client('acm', config=my_config)
certificate = acm_client.request_certificate(
    DomainName='threetier.link',
    ValidationMethod='DNS',
    DomainValidationOptions=[
        {
            'DomainName': 'threetier.link',
            'ValidationDomain': 'threetier.link'
        },
    ],
)
# resource_ids['web_lb_acm'] = certificate['ARN']
response = elb_client.create_listener(
    LoadBalancerArn=resource_arns['web_lb'],
    Protocol='HTTPS',
    Port=443,
    SslPolicy='ELBSecurityPolicy-2016-08',
    Certificates=[
        {
            # resource_ids['web_lb_acm']
            'CertificateArn': 'arn:aws:acm:ap-northeast-2:999822656998:certificate/45c7b093-b8a7-41ce-9430-a7ae803b3938',
        },
    ],
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': resource_arns['was_lb_tg'],
        },
    ],
)
'''