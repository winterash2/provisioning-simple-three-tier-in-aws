import sys
import botocore
import boto3
import time

class VPC:

    # 클래스 생성 시 호출되는 초기화 함수, boto3Interfaces를 통해 미리 생성한 ec2_clinet를 전달받음
    def __init__(self):
        print("Class VPC")
