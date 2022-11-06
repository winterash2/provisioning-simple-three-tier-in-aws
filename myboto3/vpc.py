import sys
import botocore
import boto3
from myboto3.subnet import Subnet
from myboto3.routetable import RouteTable

class VPC:
    '''
        _id
        _CidrBlock
        _subnetPublicDefault01
        _subnetPublicDefault02
        _internetGatewayID
        _natGatewayID
        _publicRouteTable
        _priaveteRouteTable
        _natRouteTable
    '''

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def CidrBlock(self):
        return self._CidrBlock
    
    @CidrBlock.setter
    def CidrBlock(self, value):
        self._CidrBlock = value

    # 클래스 생성 시 호출되는 초기화 함수, boto3Interfaces를 통해 미리 생성한 ec2_clinet를 전달받음
    def __init__(self, boto3Interfaces, CidrBlock = '10.0.0.0/16'):
        self._CidrBlock = CidrBlock # Boto3의 옵션과 혼동되지 않도록 네이밍을 동일하게 함
        self._boto3Interfaces = boto3Interfaces
        self._ec2_resource = boto3Interfaces['ec2_resource']
        self._ec2_client = boto3Interfaces['ec2_client']
        self._id = None

        threetierVpc = self._ec2_resource.create_vpc(
            CidrBlock = self._CidrBlock,
        )
        self._id = threetierVpc.id

        print("VPC 생성")

        # Default Subnet 생성
        self._subnetPublicDefault01 = Subnet(boto3Interfaces=self._boto3Interfaces, Vpc=self, AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.0.0/24')
        self._subnetPublicDefault01.createTag(Key='Name', Value='subnet_public_detault_01')
        self._subnetPublicDefault02 = Subnet(boto3Interfaces=self._boto3Interfaces, Vpc=self, AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.1.0/24')
        self._subnetPublicDefault02.createTag(Key='Name', Value='subnet_public_detault_02')

        # 인터넷 게이트웨이 생성하여 연결
        internet_gateway = self._ec2_client.create_internet_gateway()
        self._internetGatewayID = internet_gateway['InternetGateway']['InternetGatewayId']
        response = threetierVpc.attach_internet_gateway(InternetGatewayId=self._internetGatewayID)

        # NAT 게이트웨이 생성
        ## EIP 생성
        nat_eip = self._ec2_client.allocate_address(Domain='vpc')
        self._natEipId = nat_eip['AllocationId']
        #### NAT Gateway 생성
        response = self._ec2_client.create_nat_gateway(
            SubnetId=self._subnetPublicDefault01.id,
            ConnectivityType='public',
            AllocationId=self._natEipId
        )
        self._natGatewayID = response['NatGateway']['NatGatewayId']
        
        print("NAT 게이트웨이 생성이 완료될때까지 기다려주세요. 계속하시려면 Enter를 입력하시오")
        input()

        # Public 라우트 테이블 생성
        self._publicRouteTable = RouteTable(boto3Interfaces=self._boto3Interfaces, Vpc=self)
        self._publicRouteTable.makePublic()
        # Private 라우트 테이블 생성
        self._priaveteRouteTable = RouteTable(boto3Interfaces=self._boto3Interfaces, Vpc=self)
        # NAT 라우트 테이블 생성
        self._natRouteTable = RouteTable(boto3Interfaces=self._boto3Interfaces, Vpc=self)
        self._natRouteTable.makeNat()

    def delete(self):
        # 라우트 테이블 제거
        self._natRouteTable.delete()
        self._priaveteRouteTable.delete()
        self._publicRouteTable.delete()
        # Nat 게이트웨이 제거 및 연결된 EIP 제거
        self._ec2_client.delete_nat_gateway(
            NatGatewayId=self._natGatewayID
        )
        print("NAT 게이트웨이 제거가 완료될때까지 기다려주세요. 계속하시려면 Enter를 입력하시오")
        input()
        self._ec2_client.release_address(
            AllocationId=self._natEipId,
        )

        # Internet Gateway를 VPC에서 분리 및 제거
        self._ec2_client.detach_internet_gateway(
            InternetGatewayId=self._internetGatewayID,
            VpcId=self._id
        )
        self._ec2_client.delete_internet_gateway(
            InternetGatewayId=self._internetGatewayID
        )
        # Default 서브넷 제거
        self._subnetPublicDefault01.delete()
        self._subnetPublicDefault02.delete()

        response = self._ec2_client.delete_vpc(
            VpcId=self._id,
        )
        print("VPC 정상적으로 삭제하였습니다.")
        return True
    