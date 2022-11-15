#!/usr/bin/env python

import sys
import os
import botocore
import boto3
import yaml
from simpleboto3 import SimpleBoto3


def _parse_configure():
    pass


def _parse_vpc():
    pass


# 일단 kubectl처럼 사용할 수 있게끔 구현을 하려고 함. (구현할 때 단위테스트에 더 편리하고 확장성도 높다고 생각함)
# 그리고 3 Tier 구성을 하는건 별도의 파이썬 코드를 짜거나(kubectl 처럼 쓸 수 있게 만들어놓은 메서드들 사용) 
# 아니면 단순히 명령어를 나열한 쉘 스크립트로 만들거나
def _parse(argvs):
    if argvs[0].lower() == 'configure':
        _parse_configure(argvs[1:])
    if argvs[0].lower() == 'vpc':
        _parse_vpc(argvs[1:])


def _get_sts_session():
    # simpleboto3라는 이름의 프로파일을 사용
    # ~/.aws/config 에 있는 설정으로 세션 생성
    # ~/.aws/config 에 role도 설정했기 때문에 assumeRole로 role의 권한을 가져옴
    session = boto3.Session(profile_name='simpleboto3')

    # 세션이 문제없이 동작하는지 테스트
    try:
        ec2_client = session.client('ec2')
        CredentialTest = ec2_client.create_vpc(CidrBlock='10.0.0.0/16', DryRun=True)
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'AuthFailure':
            print("AWS 자격증명에 문제가 있습니다. 계정을 확인해주시기 바랍니다.")
            return None
        elif err.response['Error']['Code'] == 'DryRunOperation':
            pass
        else: # DryRun으로 실행했기 때문에 반드시 except가 발생해야 함. 발생하지 않은 경우 문제가 있는 것으로 판단
            return None
    
    return session


def main():
    if len(sys.argv) == 1:
        pass # help 넣을 것
    else:
        _parse(sys.argv[1:])
    
    session = _get_sts_session()
    simpleBoto3 = SimpleBoto3(session)

    '''
    VPC
    ./simpleBoto3.py get vpc                                                    # VPC들을 출력
    ./simpleBoto3.py create vpc VPC_NAME                                        # VPC 생성
    ./simpleBoto3.py describe vpc VPC_NAME                                      # VPC 정보 출력
    '''
    simpleBoto3.create_vpc()
    
    
    # 

    # print(sys.argv[0])
    # file_path = sys.argv[1]

    # if len(sys.argv) != 2:
    #     print("Insufficient arguments")
    #     sys.exit()

    # print("File path : " + file_path)
    

if __name__ == "__main__":
    main()
