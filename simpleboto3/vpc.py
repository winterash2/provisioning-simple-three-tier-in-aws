import sys
import botocore
import boto3
import time
from tag import *

class VPC:
    # VPC ID
    _name = None
    _id = None

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value


    # 클래스 생성 시 호출되는 초기화 함수, boto3Interfaces를 통해 미리 생성한 ec2_clinet를 전달받음
    def __init__(self):
        print("Class VPC")


    def delete_vpc(self):
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


    def create_vpc(self, simpleBoto3, cidrBlock = '10.0.0.0/16'):
        # VPC 생성
        try:
            response = simpleBoto3.ec2_resource.create_vpc(
                CidrBlock = cidrBlock,
            )
            self._id = response.id
        except Exception as err:
            print("VPC 생성 중 알 수 없는 에러가 발생하였습니다.", str(err))
            raise
        # VPC 생성 후 namespace 태그 생성. 문제 발생 시 VPC도 제거
        try:
            ec2_create_tag(resource=self, key='simpleBoto3', value=simpleBoto3.namespace)
        except Exception as err:
            print("VPC에 Tag 생성 중 알 수 없는 에러가 발생하였습니다.")
            self.delete_vpc()
            raise

    
def get_vpc_id_from_namespace(self, namespace):
    # 먼저 해당 namespace에 해당하는 vpc가 있는지
    try:
        response = self._ec2_client.describe_vpcs(
            Filters=[{'Name': 'simpleBoto3', 'Values': [namespace,]},],)
    except Exception as err:
        print("알 수 없는 에러가 발생하였습니다.", str(err))
        raise
    
    # 만약 vpc가 생성되어 있는 경우
    if len(response['Vpcs']) == 1:
        self._vpc = VPC.id = response['Vpcs'][0]['VpcId']
    elif len(response['Vpcs']) == 0: # VPC가 없는 경우
        return None
    else: # 같은 namespace에 여러 vpc가 있는 경우
        raise Exception("같은 네임스페이스에 여러 VPC가 존재합니다.")
