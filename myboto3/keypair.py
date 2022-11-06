import sys
import botocore
import boto3

class KeyPair:
    '''
        _keyName
    '''

    @property
    def Name(self):
        return self._Name
    
    @Name.setter
    def Name(self, value):
        self._Name = value

    # 클래스 생성 시 호출되는 초기화 함수, boto3Interfaces를 통해 미리 생성한 ec2_clinet를 전달받음
    def __init__(self, boto3Interfaces, keyName = 'keypair'):
        self._keyName = keyName # Boto3의 옵션과 혼동되지 않도록 네이밍을 동일하게 함
        self._ec2_resource = boto3Interfaces['ec2_resource']
        self._ec2_client = boto3Interfaces['ec2_client']
    
    def create(self):
        try:
            key_pair = self._ec2_resource.create_key_pair(KeyName=self._keyName)
            keypair_file = open(self._keyName+'.pem', 'w')
            keypair_file.write(str(key_pair.key_material))
            keypair_file.close()
        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
                print(self._keyName, " 키를 소유하고 있습니다. 해당 키를 사용해주시기 바랍니다.")
            else:
                print("KeyPair 생성 중 알 수 없는 에러가 발생했습니다.")
                raise
    
    def delete(self):
        try:
            self._ec2_client.delete_key_pair(
                KeyName = self._keyName,
            )
            print("KeyPair", self._keyName, "정상적으로 삭제하였습니다")
        except:
            print("Unexpected error:", sys.exc_info())
            return False
        return True