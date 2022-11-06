import sys
import botocore
import boto3
import time
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
        self._subnetPublicDefault01 = Subnet(boto3Interfaces=self._boto3Interfaces, Vpc=self, AvailabilityZone='ap-northeast-2a', CidrBlock='10.0.0.0/24', Name='subnet_public_detault_01')
        self._subnetPublicDefault02 = Subnet(boto3Interfaces=self._boto3Interfaces, Vpc=self, AvailabilityZone='ap-northeast-2c', CidrBlock='10.0.1.0/24', Name='subnet_public_detault_02')

        # 인터넷 게이트웨이 생성하여 연결
        try:
            internet_gateway = self._ec2_client.create_internet_gateway()
            self._internetGatewayID = internet_gateway['InternetGateway']['InternetGatewayId']
            response = threetierVpc.attach_internet_gateway(InternetGatewayId=self._internetGatewayID)
        except botocore.exceptions.ClientError as err:
            print("Internet Gateway 생성 중 AWS 에러가 발생했습니다.")
            self._delete_vpc()
            raise
        except Exception as err:
            print("Internet Gateway 생성 중 알 수 없는 에러가 발생했습니다.")
            self._delete_vpc()
            raise
        
        # NAT 게이트웨이 생성
        ## EIP 생성
        try:
            nat_eip = self._ec2_client.allocate_address(Domain='vpc')
            self._natEipId = nat_eip['AllocationId']
        except:
            print("NAT 게이트웨이에서 사용할 EIP 생성 중 에러 발생함")
            self._delete_internet_gateway()
            self._delete_vpc()
            raise
        #### NAT Gateway 생성
        try:
            response = self._ec2_client.create_nat_gateway(
                SubnetId=self._subnetPublicDefault01.id,
                ConnectivityType='public',
                AllocationId=self._natEipId
            )
            self._natGatewayID = response['NatGateway']['NatGatewayId']
        except botocore.exceptions.ClientError as err:
            print(err.response['Error']['Code'])
            print("NAT 게이트웨이 생성 중 AWS 에러가 발생했습니다.")
            raise
        except Exception as err:
            print(" NAT 게이트웨이 생성 중 알 수 없는 이유로 에러가 발생했습니다.")
            self._delete_internet_gateway()
            self._delete_vpc()
            raise
        print("NAT 게이트웨이 생성중입니다. 이 과정은 3분가량 소요될 수 있습니다.")

        # NAT 게이트웨이 생성이 끝나는 것을 대기
        is_created = False
        while not is_created:
            try:
                status = self._get_nat_gateway_status()
                if status == 'available':
                    is_created = True
                else:
                    print("NAT 게이트웨이 현재 상태는", status, "입니다.")
                    time.sleep(30)
            except Exception as err:
                print("NAT 게이트웨이 상태 확인 중 알 수 없는 이유로 에러가 발생했습니다.")
                self._delete_nat_gateway()
                self._delete_vpc()
                raise

        # VPC에서 기본적으로 사용할 3가지 종류의 라우트 테이블을 생성함
        try:
            # Private 라우트 테이블 생성
            self._priaveteRouteTable = RouteTable(boto3Interfaces=self._boto3Interfaces, Vpc=self)
            # Public 라우트 테이블 생성
            self._publicRouteTable = RouteTable(boto3Interfaces=self._boto3Interfaces, Vpc=self)
            self._publicRouteTable.make_public()
            # NAT 라우트 테이블 생성
            self._natRouteTable = RouteTable(boto3Interfaces=self._boto3Interfaces, Vpc=self)
            self._natRouteTable.make_nat()
        except:
            print("라우트 테이블 생성 중 알 수 없는 에러가 발생했습니다.")
            self.delete_all()


    # VPC 구성 요소 전부 제거
    def delete_all(self):
        self._delete_nat_gateway()
        self._delete_internet_gateway()
        self._delete_vpc()


    # Internet Gateway 제거
    def _delete_internet_gateway(self):
        # Internet Gateway를 VPC에서 분리 및 제거
        try:
            self._ec2_client.detach_internet_gateway(
                InternetGatewayId=self._internetGatewayID,
                VpcId=self.id
            )
            time.sleep(10)
            self._ec2_client.delete_internet_gateway(
                InternetGatewayId=self._internetGatewayID
            )
        except:
            print("인터넷 게이트웨이 제거 중 알 수 없는 이유로 에러가 발생했습니다. 모든 자원을 수동으로 제거해주시기 바랍니다.")
            raise
        print("인터넷 게이트웨이를 정상적으로 제거하였습니다.")


    # Nat 게이트웨이 제거 및 연결된 EIP 제거
    def _delete_nat_gateway(self):
        
        print("NAT 게이트웨이 제거중입니다. 3분 이상의 시간이 걸릴 수 있습니다.")
        # NAT 게이트웨이 제거
        try:
            self._ec2_client.delete_nat_gateway(
                NatGatewayId=self._natGatewayID
            )
            is_removed = True
        except Exception as err:
            print("알 수 없는 이유로 NAT 게이트웨이가 제거되지 않습니다. 모든 자원을 수동으로 제거해주시기 바랍니다.")
            raise

        # NAT 게이트웨이 정상 제거됨을 확인
        is_removed = False
        count = 0
        while not is_removed:
            try:
                status = self._get_nat_gateway_status()
                if status == 'deleted':
                    is_removed = True
                else:
                    time.sleep(30)
                    count += 1
                    if count >= 10:
                        raise Exception()
            except Exception as err:
                print("알 수 없는 이유로 NAT 게이트웨이가 제거되지 않습니다. 모든 자원을 수동으로 제거해주시기 바랍니다.")
                raise

        # NAT 게이트웨이에서 사용한 EIP 제거
        try:
            self._ec2_client.release_address(
                AllocationId=self._natEipId,
            )
            time.sleep(10)
        except Exception as err:
            print("알 수 없는 이유로 EIP가 제거되지 않습니다. 모든 자원을 수동으로 제거해주시기 바랍니다.")
            print("EIP ID =", self._natEipId)
            raise
        print("NAT 게이트웨이를 정상적으로 제거하였습니다.")
    

    # VPC 제거
    def _delete_vpc(self):
        is_removed = False
        print("VPC 제거중입니다. 종속성 문제로 인하여 오랜 시간이 걸릴 수 있습니다.")
        while not is_removed:
            try:
                response = self._ec2_client.delete_vpc(
                    VpcId=self.id,
                )
                is_removed = True
            except botocore.exceptions.ClientError as err:
                print(err.response['Error']['Code'])
                print("VPC 제거중입니다. 10번 이상 메시지가 반복되면 프로그램을 종료하고 수동으로 제거 부탁드립니다.")
                print("VPC가 콘솔에서는 잘 지워지지만 boto3 API로는 계속 DependencyViolation 에러가 발생하는 현상이 있습니다. 가급적 프로그램을 종료하고 콘솔에서 제거해주시기 바랍니다.")
                print("VPC ID =", self.id)
                time.sleep(60)
            except Exception as err:
                print("알 수 없는 이유로 VPC가 제거되지 않습니다. 모든 자원을 수동으로 제거해주시기 바랍니다.")
        print("VPC를 정상적으로 제거하였습니다.")


    # NAT Gateway 상태 return
    def _get_nat_gateway_status(self):
        # NAT 게이트웨이 상태 코드 리턴
        try:
            response = self._ec2_client.describe_nat_gateways(
                NatGatewayIds=[
                    self._natGatewayID,
                ],
            )
            return response['NatGateways'][0].get('State')
        except botocore.exceptions.ClientError as err:
            print("NAT 게이트웨이 상태 확인 중 알 수 없는 에러가 발생했습니다.")
            print(err.response['Error']['Code'])
            raise
        except Exception as err:
            print("알 수 없는 이유로 에러가 발생했습니다.")
            raise