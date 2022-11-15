import sys
import os
import botocore
import boto3
import yaml
from simpleboto3.vpc import *
from simpleboto3.vpc import VPC
from simpleboto3.subnet import Subnet
from simpleboto3.securitygroup import SecurityGroup

# from vpc import VPC
# from subnet import Subnet
# from securitygroup import SecurityGroup

# 생성하는 모든 자원에 {'simpleBoto3' : '입력받은 Unique한 이름'} 태그를 붙이고, 
# 모든 자원의 {'Name' : } 태그를 전부 지정해줌으로써 
class SimpleBoto3:
    # Kubernets 처럼 namespace별로 작업. 해당 네임스페이스 내의 모든 자원은 'simpleBoto3':'namespace' 태그를 추가할 것임
    _vpcName = 'default'

    @property
    def vpcName(self):
        return self._vpcName

    # myboto3에서와 같이 일일히 boto3Interfaces=boto3Interfaces 와 같이 파라미터를 넘기는 것을 
    # 없애기 위해 SimpleBoto3 라는 클래스로 한 번 더 묶고 여기에서 session이나 client 등을 관리
    _session = None
    _ec2_client = None

    @property
    def session(self):
        return self._session
    
    @session.setter
    def session(self, value):
        self._session = value

    @property
    def ec2_client(self):
        return self._ec2_client

    @property
    def ec2_resource(self):
        return self._ec2_resource
    

    # {'simpleBoto3' : name} 태그를 달고 있는 모든 자원을 simpleBoto3 라는 객체에서 전부 가지고 있음으로써 사용을 편리하게 함
    # 자원의 사용은 전부 Name으로 할 수 있도록 함
    _vpc = None # VPC 클래스 보관
    _subnets = {} # Subnet 클래스들 보관
    _securityGroups = {} # SecurityGroup 클래스들 보관
    

    def __init__(self, session, vpcName='default'):
        # session, 각종 client들 생성하여 내부 변수에 저장
        self._session = session
        self._vpcName = vpcName
        self._ec2_client = session.client('ec2')
        self._ec2_resource = session.resource('ec2')


    def create_vpc(self):
        self._vpc = VPC(simpleBoto3=self ,name=self._vpcName)
        # 먼저 해당이름의 VPC가 있는지부터 확인
        self._vpc.id = self._vpc.get_vpc_id_from_vpcName(self, vpcName=self.vpcName)
        if self._vpc.id != None: # VPC가 이미 있는 경우
            print(self.vpcName, "이름의 VPC가 이미 생성되어 있습니다.")
        else:
            self._vpc.create_vpc(cidrBlock = '10.0.0.0/16')


    def describe_vpc(self):
        print()


    def test_subent(self):
        test = Subnet()
        

    def set_vpc_options():
        pass


    def describe_vpc(self, cidrBlock='10.0.0.0/16'):
        pass


    def get_subnet_list(self):
        pass

    # type 파라미터는 
    def create_subnet(self, name, cidrBlock, type='public'):
        pass

    # 보안 그룹은 따로 생성하도록 하지 말고, 각 자원을 생성할 때(예: Bastion 인스턴스 생성), 
    # 그에 들어가는 default 보안그룹을 생성
    # 사용자가 보안 그룹을 따로 만드는건 불가능하게끔함
    # def accept_tcp_from_to(self, source, destination):
    #     if type(source) == Subnet:
    #         pass
    #     elif type(source) == SecurityGroup:
    #         pass
