import sys
import botocore
import boto3

class SecurityGroup:

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value

    def __init__(self, boto3Interfaces, Vpc, Name):
        self._Vpc = Vpc
        self._ec2_client = boto3Interfaces['ec2_client']
        self._ec2_resource = boto3Interfaces['ec2_resource']
        self._Tags = []
        self._Name = Name

        response = self._ec2_resource.create_security_group(
            Description=Name,
            GroupName=Name,
            VpcId=self._Vpc._id
        )
        self._id = response.id
        self._sg_client = self._ec2_resource.SecurityGroup(self._id)
    
    def delete(self):
        self._ec2_client.delete_security_group(
            GroupId=self._id,
        )

    def accept_tcp_from_cidr(self, From, To, CidrIp, Description):
        response = self._sg_client.authorize_ingress(
            IpPermissions=[
                {
                    'FromPort': From,
                    'IpProtocol': 'tcp',
                    'ToPort': To,
                    'IpRanges': [
                        {
                            'CidrIp': CidrIp,
                            'Description': Description
                        },
                    ],
                },
            ],
        )

    def accept_tcp_from_security_group(self, From, To, securityGroup, Description):
        response = self._sg_client.authorize_ingress(
            IpPermissions=[
                {
                    'FromPort': From,
                    'IpProtocol': 'tcp',
                    'ToPort': To,
                    "UserIdGroupPairs": [
                        {
                            'GroupId': securityGroup._id, 
                            'Description': Description
                        }
                    ]
                },
            ],
        )