import os
import botocore
import boto3
import yaml

# 실행하면서 생성된 변수들에 대한 정보를 저장할 cache 폴더를 생성
def createCacheFoler():
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")
    except:
        # 프로그램을 실행시킨 OS 계정에 문제가 있는 경우
        print("현재 폴더와 하위 폴더에 파일을 읽고 쓸 수 있는 권한을 가진 계정으로 다시 실행하십시오.")

def createBoto3Session(globalConfig):
    session = boto3.Session(
        aws_access_key_id=globalConfig['ACCESS_KEY'],
        aws_secret_access_key=globalConfig['SECRET_KEY']
    )
    my_config = botocore.config.Config(
        region_name = globalConfig['AWS_REGION_NAME'],
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    # ACCESS_KEY와 SECRET_KEY가 유효한지 확인
    try:
        ec2_client = session.client('ec2', config=my_config)
        CredentialTest = ec2_client.create_vpc(CidrBlock='10.0.0.0/16', DryRun=True)
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'AuthFailure':
            print("AWS 자격증명에 문제가 있습니다. config.yaml 파일의 ACCESS_KEY와 SECRET_KEY를 확인해주시기 바랍니다.")
            return None
        elif err.response['Error']['Code'] == 'DryRunOperation':
            return session
    return None # DryRun으로 실행했기 때문에 반드시 except가 발생해야 함. 발생하지 않은 경우 문제가 있는 것으로 판단

def loadConfigFile():
    with open('testconfig.yaml') as f:
        globalConfig = yaml.safe_load(f)
    return globalConfig

def main():
    globalConfig = loadConfigFile()

    # 실행을 시작하기 전 환경 구성 및 검증
    createCacheFoler()

    # boto3 session 생성, 문제가 있으면 프로그램 종료
    session = createBoto3Session(globalConfig)
    if session == None:
        return 1
    
    

if __name__ == "__main__":
    main()
