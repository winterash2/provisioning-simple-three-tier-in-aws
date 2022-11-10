#!/usr/bin/env python

import sys
import os
import botocore
import boto3
import yaml
from simpleboto3 import SimpleBoto3


# AssumeRole을 이용하여 자격증명을 할 수 있도록 ~/.aws/config에 설정값을 추가할 수 있도록?
# aws configure --profile testUser

# EKS 사용할 때, kubectl 내용 중 일부
# - name: <EKS 클러스터 ARN>
#   user:
#     exec:
#       apiVersion: client.authentication.k8s.io/v1beta1
#       args:
#       - --region
#       - ap-northeast-2
#       - eks
#       - get-token
#       - --cluster-name
#       - <EKS 클러스터 이름>
#       - --role
#       - <EKS 클러스터 생성 시 설정했던 Role의 ARN>
#       command: aws
# 자격증명에 사용되면 명령어는 aws --region ap-northeast-2 eks get-token --cluster-name <EKS 클러스터 이름> --role <Role ARN) 으로 보임
# 이거 대신에 sts 토큰 가져오는 명령어는?

# https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_credentials_temp_use-resources.html#using-temp-creds-sdk-cli
    # AWS CLI에서 임시 보안 자격 증명 사용
    # AWS CLI에서 임시 보안 자격 증명을 사용할 수 있습니다. 이 임시 보안 자격 증명은 정책을 테스트하는 데 유용합니다.

    # AWS CLI를 사용하여 AssumeRole 또는 GetFederationToken과 같은 AWS STS API를 호출한 다음 결과 출력을 캡처할 수 있습니다. 다음 예는 파일에 출력을 전송하는 AssumeRole에 대한 호출을 보여줍니다. 이 예제에서 profile 파라미터는 AWS CLI 구성 파일의 프로파일로 간주됩니다. 또한 역할을 수임할 권한이 있는 IAM 사용자의 자격 증명을 참조하는 것으로 간주됩니다.

    # aws sts assume-role --role-arn arn:aws:iam::123456789012:role/role-name --role-session-name "RoleSession1" --profile IAM-user-name > assume-role-output.txt
    # 명령이 끝나면 라우팅한 위치에서 액세스 키 ID, 보안 액세스 키 및 세션 토큰을 추출할 수 있습니다. 수동으로 또는 스크립트를 사용하여 이 작업을 수행할 수 있습니다. 그런 다음 이 값을 환경 변수에 할당할 수 있습니다.

    # AWS CLI 명령을 실행할 때 AWS CLI는 환경 변수로 시작하여 구성 파일로 넘어가는 특정 순서로 자격 증명을 찾습니다. 따라서 임시 자격 증명을 환경 변수에 넣은 후에 AWS CLI는 그 자격 증명을 기본 값으로 사용합니다. (명령에 profile 파라미터를 지정한다면 AWS CLI는 환경 변수를 건너뜁니다. 대신 AWS CLI는 구성 파일을 검색합니다. 이로써 필요한 경우 환경 변수에서 자격 증명을 무시할 수 있게 됩니다.)

    # 다음 예는 임시 보안 자격 증명에 대한 환경 변수를 설정한 다음, AWS CLI 명령을 호출하는 방법을 보여줍니다. profile 파라미터는 AWS CLI 명령에 포함되어 있지 않기 때문에 AWS CLI는 먼저 환경 변수에서 자격 증명을 검색하고, 따라서 임시 자격 증명을 사용합니다.

    # Linux

    # $ export AWS_ACCESS_KEY_ID=ASIAIOSFODNN7EXAMPLE
    # $ export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    # $ export AWS_SESSION_TOKEN=AQoDYXdzEJr...<remainder of session token>
    # $ aws ec2 describe-instances --region us-west-1

# 여기 참고 https://dev.classmethod.jp/articles/aws-cli-iam-role-switch-kr/
# aws sts assume-role --role-arn arn:aws:iam::yyyyyyyyyyyy:role/역할명 --role-session-name 아무거나 --serial-number arn:aws:iam::xxxxxxxxxxxx:mfa/사용자명 --token-code MFA인증번호
# 이렇게 요청하면

# {
#   "Credentials": {
#     "AccessKeyId": "ZZZZZZZZZZZZZZZZZZZZZ",
#     "SecretAccessKey": "~",
#     "SessionToken": "시크릿 액세스 키를 초월하는 엄청나게 긴 문자열이 나옵니다",
#     "Expiration": "2020-07-28T12:15:05+00:00"
#   },
#   "AssumedRoleUser": {
#     "AssumedRoleId": "OOOOOOOOOOOOOOOOOOOOO:세션명",
#     "Arn": "arn:aws:sts::yyyyyyyyyyyy:assumed-role/역할명/세션명"
#   }
# }
# 이런 결과가 나오는데 그 중 아래와 같이 세 개를 쓰면 임시로 쓸 수 있는 키가 나옴
# export AWS_ACCESS_KEY_ID=위에 출력된 액세스 키
# export AWS_SECRET_ACCESS_KEY=위에 출력된 액세스 키
# export AWS_SESSION_TOKEN=위에 출력된 세션 토큰

# AssumeRole 쓰는 이유
# https://brunch.co.kr/@topasvga/1201
# https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_roles_create_for-user.html
# Role을 이용하면
# 권한 부여가 더 간단해질 것 같음 - Role에 어떤 것을 하기 위해 필요한 권한들을 다 넣어놓고, 사용자에게는 해당 role을 assumeRole이
# 가능하게끔 하면 나중에 이 작업을 못하게 다시 뺄 때는 Role만 빼주면 됨. 그게 아니면 흩어져있는 권한들을 일일히 검토해야 함
# role arn을 모르면 못 쓸 것 같음 - assumeRole을 사용하는 경우 assumeRole의 ARN도 입력하게 되어있음. 따라서 ACCESS KEY와 SECRET KEY
# 이렇게 두개 외에도 role의 arn도 알아야 쓸 수 있음
# 사용할 때 role arn으로 role에 대한 권한을 얻어서 사용함. 그래서 만약 ec2와 s3를 각각 사용할 수 있는 role을 두 개 부여받았을 때, 
# 그냥 권한을 넣어줬을 때는 2개를 조합해서도 쓰고 그럴 수 있지만, assumeRole을 사용할 경우에는 그게 불가능할 것 같음.


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
    '''
    https://tech.cloud.nongshim.co.kr/2021/03/12/boto3%EA%B0%80-aws%EC%9D%98-%EC%9E%90%EA%B2%A9%EC%A6%9D%EB%AA%85credentials%EC%9D%84-%ED%99%95%EC%9D%B8%ED%95%98%EB%8A%94-%EC%88%9C%EC%84%9C-from-python/

    [profile test-profile5]
    output = json
    region = ap-northeast-2
    role_arn = YOUR_ROLE_ARN1 ; [ARN of Role with AssumeRole authority of STS service]
    credential_source = Ec2InstanceMetadata

    [profile test-profile6]
    output = json
    region = ap-northeast-2
    role_arn = YOUR_ROLE_ARN2 ; [ARN of the role you want to create with AssumeRole]
    source_profile  = test-profile5 # STS AssumeRole 권한은 test-profile5 에서 얻어오게 하는 설정이라고 함
    role_session_name = NDS-session-1st

    ~/.aws/config 에 있는 설정파일들을 이용하도록 할 것임
    사용자에게는 aws-cli 설치와 aws configure --profile simpleboto3 명령어로 credential과 config를 설정할 수 있도록 함
    role_arn 은 aws cli로 설정이 불가능함. 따라서 사용 설명서에 방법을 안내해야 할 것 같음
    
    '''

    # ~/.aws/config 에 있는 설정으로 AssumeRole 호출
    session = boto3.Session(profile_name='simpleboto3')

    # STS 클라이언트 객체를 만들고 assume_role을 호출하여 임시 자격증명을 가져옴
    # Role Arn도 어디선가 입력을 받아야 함. 설정파일을 이용해야 할 것 같음
    try:
        sts_client = session.client('sts')
        assumeRoleObject = sts_client.assume_role(
            RoleArn='',
            # 역할 신뢰 정책에서 RoleSessionName 키를 사용하여 사용자가 역할을 수임할 때 특정 세션 이름을 지정하도록 요구할 수 있습니다.
            # 예를 들어 IAM 사용자가 자신의 사용자 이름을 세션 이름으로 지정하도록 요구할 수 있습니다.
            # IAM 사용자가 역할을 수임하면 사용자 이름과 일치하는 세션 이름과 함께 AWS CloudTrail 로그에 활동이 나타납니다. 
            # 이렇게 하면 여러 보안 주체가 한 역할을 사용할 때 관리자가 역할 세션 간을 구분하는 것이 쉬워집니다.
            # 다만 아래와 같이 aws:username 조건 변수를 사용하면 임시 자격 증명을 사용하는 사용자가 역할을 수임할 수 없음. username 변수는 IAM 사용자에게만 사용되기 때문
            # {
            #     "Version": "2012-10-17",
            #     "Statement": [
            #         {
            #             "Sid": "RoleTrustPolicyRequireUsernameForSessionName",
            #             "Effect": "Allow",
            #             "Action": "sts:AssumeRole",
            #             "Principal": {"AWS": "arn:aws:iam::111122223333:root"},
            #             "Condition": {
            #                 "StringLike": {"sts:RoleSessionName": "${aws:username}"}
            #             }
            #         }
            #     ]
            # }
            RoleSessionName=''
        )
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'AuthFailure':
            print("AWS 자격증명에 문제가 있습니다. config.yaml 파일의 ACCESS_KEY와 SECRET_KEY를 확인해주시기 바랍니다.")
            return None
        else:
            return None
    credentials = assumeRoleObject['Credentials']
    # print(credentials)

    # 임시 자격증명을 이용하여 새로운 세션을 연결
    newSession = boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    # 새로운 세션이 문제없이 동작하는지 테스트
    try:
        ec2_client = session.client('ec2')
        CredentialTest = ec2_client.create_vpc(CidrBlock='10.0.0.0/16', DryRun=True)
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'AuthFailure':
            print("AWS 자격증명에 문제가 있습니다. config.yaml 파일의 ACCESS_KEY와 SECRET_KEY를 확인해주시기 바랍니다.")
            return None
        elif err.response['Error']['Code'] == 'DryRunOperation':
            pass
        else: # DryRun으로 실행했기 때문에 반드시 except가 발생해야 함. 발생하지 않은 경우 문제가 있는 것으로 판단
            return None

    return newSession


def main():
    if len(sys.argv) == 1:
        print("help 넣을 것")
    else:
        _parse(sys.argv[1:])
    
    simpleBoto3 = SimpleBoto3()

    # 

    # print(sys.argv[0])
    # file_path = sys.argv[1]

    # if len(sys.argv) != 2:
    #     print("Insufficient arguments")
    #     sys.exit()

    # print("File path : " + file_path)
    

if __name__ == "__main__":
    main()
