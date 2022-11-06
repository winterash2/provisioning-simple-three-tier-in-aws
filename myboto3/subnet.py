import sys
import botocore
import boto3

class Subnet:

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

    @property
    def AvailabilityZone(self):
        return self._AvailabilityZone
    
    @AvailabilityZone.setter
    def AvailabilityZone(self, value):
        self._AvailabilityZone = value

    # 클래스 생성 시 호출되는 초기화 함수, boto3Interfaces를 통해 미리 생성한 ec2_clinet를 전달받음
    def __init__(self, boto3Interfaces, Vpc, AvailabilityZone, CidrBlock, Name):
        self._Vpc = Vpc
        self._AvailabilityZone = AvailabilityZone
        self._CidrBlock = CidrBlock
        self._ec2_client = boto3Interfaces['ec2_client']
        self._ec2_resource = boto3Interfaces['ec2_resource']
        self._id = None
        self._Tags = []
        self._Name = Name

        print("Subnet 생성", AvailabilityZone, CidrBlock)

        vpc_client = self._ec2_resource.Vpc(self._Vpc._id)
        response = vpc_client.create_subnet(
            AvailabilityZone = self._AvailabilityZone, 
            CidrBlock = self._CidrBlock
        )
        response = self._ec2_client.create_tags(
            Resources = [self._id],
            Tags = [{'Key': 'Name', "Value": Name}],
        )

        self._id = response.id

    def delete(self):
        response = self._ec2_client.delete_subnet(
            SubnetId=self._id, # subnet_private_was_lb_01
        )

    def make_public(self):
        response = self._ec2_client.associate_route_table(
            RouteTableId=self._Vpc._publicRouteTable._id,
            SubnetId=self._id,
        )
    
    def make_private(self):
        response = self._ec2_client.associate_route_table(
            RouteTableId=self._Vpc._priaveteRouteTable._id,
            SubnetId=self._id,
        )

    def make_nat(self):
        response = self._ec2_client.associate_route_table(
            RouteTableId=self._Vpc._natRouteTable._id,
            SubnetId=self._id,
        )