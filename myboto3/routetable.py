import sys
import botocore
import boto3
# import myboto3.vpc

class RouteTable:

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def Name(self):
        return self._Name
    
    @Name.setter
    def Name(self, value):
        self._Name = value

    # 클래스 생성 시 호출되는 초기화 함수, boto3Interfaces를 통해 미리 생성한 ec2_clinet를 전달받음
    def __init__(self, boto3Interfaces, Vpc):
        self._Vpc = Vpc
        self._ec2_resource = boto3Interfaces['ec2_resource']
        self._ec2_client = boto3Interfaces['ec2_client']
        
        response = self._ec2_resource.create_route_table(VpcId=self._Vpc.id,)
        self._id = response.id
    
    def delete(self):
        response = self._ec2_client.delete_route_table(
            RouteTableId=self.id
        )
        return True

    def make_public(self):
        response = self._ec2_client.create_route(
            DestinationCidrBlock = '0.0.0.0/0',
            GatewayId = self._Vpc._internetGatewayID,
            RouteTableId = self.id,
        )
        return self

    def make_nat(self):
        route_private_with_nat = self._ec2_client.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=self._Vpc._natGatewayID,
            RouteTableId=self.id,
        )
        return self
