import os
import botocore
import boto3
import yaml
from myboto3.vpc import VPC
from myboto3.subnet import Subnet
from myboto3.routetable import RouteTable
from myboto3.securitygroup import SecurityGroup
from myboto3.keypair import KeyPair
from myboto3.rds import RDS

global globalConfig

# 실행하면서 생성된 변수들에 대한 정보를 저장할 cache 폴더를 생성
def createCacheFoler():
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")
    except:
        # 프로그램을 실행시킨 OS 계정에 문제가 있는 경우
        print("현재 폴더와 하위 폴더에 파일을 읽고 쓸 수 있는 권한을 가진 계정으로 다시 실행하십시오.")

def createBoto3Interfaces(globalConfig):
    session = boto3.Session(
        aws_access_key_id=globalConfig['ACCESS_KEY'],
        aws_secret_access_key=globalConfig['SECRET_KEY']
    )
    my_config = botocore.config.Config(
        region_name = globalConfig['AWS_REGION_NAME'],
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    # ACCESS_KEY와 SECRET_KEY가 유효한지 확인
    try:
        ec2_client = session.client('ec2', config=my_config)
        CredentialTest = ec2_client.create_vpc(CidrBlock='10.0.0.0/16', DryRun=True)
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'AuthFailure':
            print("AWS 자격증명에 문제가 있습니다. config.yaml 파일의 ACCESS_KEY와 SECRET_KEY를 확인해주시기 바랍니다.")
            return None
        elif err.response['Error']['Code'] == 'DryRunOperation':
            pass
        else: # DryRun으로 실행했기 때문에 반드시 except가 발생해야 함. 발생하지 않은 경우 문제가 있는 것으로 판단
            return None
    
    boto3Interfaces = {}
    boto3Interfaces['ec2_client'] = session.client('ec2', config=my_config)
    boto3Interfaces['ec2_resource'] = session.resource('ec2', config=my_config)
    boto3Interfaces['rds_client'] = session.client('rds', config=my_config)
    boto3Interfaces['elb_client'] = session.client('elbv2', config=my_config)
    boto3Interfaces['asg_client'] = session.client('autoscaling', config=my_config)
    # boto3Interfaces['route53domains_client'] = session.client('route53domains', region_name='us-east-1')
    boto3Interfaces['acm_client'] = session.client('acm', config=my_config)

    return boto3Interfaces 

# config.yaml에 입력되어 있는 설정값들 로드
def loadConfigFile():
    with open('config.yaml') as f:
        globalConfig = yaml.safe_load(f)
    return globalConfig

def main():
    global globalConfig
    globalConfig = loadConfigFile()

    # 실행을 시작하기 전 환경 구성 및 검증
    createCacheFoler()

    # boto3 session 생성, 문제가 있으면 프로그램 종료
    boto3Interfaces = createBoto3Interfaces(globalConfig)
    if boto3Interfaces == None:
        return 1

    # VPC 생성
    threeTierVPC = VPC(boto3Interfaces, "10.0.0.0/16")
    
    # KeyPair 생성
    threeTierKeyPair = KeyPair(boto3Interfaces, keyName="defaultKeyPair")
    threeTierKeyPair.create()

    # WEB 서브넷 생성
    subnetPrivateWeb01 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.2.0/24', Name='subnet_private_web_01')
    subnetPrivateWeb02 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.3.0/24', Name='subnet_private_web_02')
    subnetPrivateWeb01.make_nat()
    subnetPrivateWeb02.make_nat()
    # WAS 서브넷 생성
    subnetPrivateWas01 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.4.0/24', Name='subnet_private_Was_01')
    subnetPrivateWas02 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.5.0/24', Name='subnet_private_Was_02')
    subnetPrivateWas01.make_nat()
    subnetPrivateWas02.make_nat()
    # DB 서브넷 생성
    subnetPrivateDb01 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.6.0/24', Name='subnet_private_Db_01')
    subnetPrivateDb02 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.7.0/24', Name='subnet_private_Db_02')
    subnetPrivateDb01.make_private()
    subnetPrivateDb02.make_private()
    # WEB LB 서브넷 생성
    subnetPublicWebLb01 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.8.0/24', Name='subnet_public_WEB_LB_01')
    subnetPublicWebLb02 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.9.0/24', Name='subnet_public_WEB_LB_02')
    subnetPublicWebLb01.make_public()
    subnetPublicWebLb02.make_public()
    # WAS LB 서브넷 생성
    subnetPrivateWasLb01 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.10.0/24', Name='subnet_Private_Was_LB_01')
    subnetPrivateWasLb02 = Subnet(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.11.0/24', Name='subnet_Private_Was_LB_02')
    subnetPrivateWasLb01.make_private()
    subnetPrivateWasLb02.make_private()

    # Bastion 보안 그룹 생성
    bastionSg = SecurityGroup(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, Name='bastionSg')
    bastionSg.accept_tcp_from_cidr(From=22, To=22, CidrIp='0.0.0.0/0', Description='Accept ssh from all')
    # WEB LB 보안 그룹 생성
    webLbSg = SecurityGroup(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, Name='webLbSg')
    webLbSg.accept_tcp_from_cidr(From=443, To=443, CidrIp="0.0.0.0/0", Description="Accept HTTPS from all")
    # WEB 보안 그룹 생성
    webSg = SecurityGroup(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, Name='webSg')
    webSg.accept_tcp_from_security_group(From=22, To=22, securityGroup=bastionSg, Description="Accept ssh from bastion")
    webSg.accept_tcp_from_security_group(From=80, To=80, securityGroup=webLbSg, Description="Accept HTTP from WEB LB")
    # WAS LB 보안 그룹 생성
    wasLbSg = SecurityGroup(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, Name='wasLbSg')
    wasLbSg.accept_tcp_from_security_group(From=80, To=80, securityGroup=webSg, Description="Accept HTTP from Web")
    # WAS 보안 그룹 생성
    wasSg = SecurityGroup(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, Name='wasSg')
    wasSg.accept_tcp_from_security_group(From=22, To=22, securityGroup=bastionSg, Description="Accept ssh from bastion")
    wasSg.accept_tcp_from_security_group(From=80, To=80, securityGroup=wasLbSg, Description="Accept HTTP from WAS LB")
    # DB(RDS) 보안 그룹 생성
    dbSg = SecurityGroup(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, Name='dbSg')
    dbSg.accept_tcp_from_security_group(From=3306, To=3306, securityGroup=wasSg, Description="Accept DB connection from WAS")

    # # RDS 생성
    # rdsMysql = RDS(boto3Interfaces=boto3Interfaces, Vpc=threeTierVPC, DBName="threetier", Subnets=[subnetPrivateDb01, subnetPrivateDb02], SecurityGroups=[dbSg], DBEngine="mysql", Version=globalConfig['MySQLVersion'])

    print("1. 모든 자원 제거")
    print("2. 프로그램 종료(모든 자원을 수동으로 제거해야 합니다.")
    print("입력: ")
    select = input()
    if select == '1':
        # rdsMysql.delete()
        threeTierVPC.delete_all()
        threeTierKeyPair.delete()
    elif select == '2':
        pass
    else:
        # rdsMysql.delete()
        threeTierVPC.delete_all()
        threeTierKeyPair.delete()

if __name__ == "__main__":
    main()
