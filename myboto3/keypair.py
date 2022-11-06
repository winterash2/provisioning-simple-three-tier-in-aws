import sys
import botocore
import boto3

class KeyPair:
    '''
    Create
        KEYPAIR_NAME = "keypair"
        keypair_file = open('keypair.pem', 'w')
        key_pair = ec2_resource.create_key_pair(KeyName=KEYPAIR_NAME)
        keypair_file.write(str(key_pair.key_material))
        keypair_file.close()
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
        except:
            print("Unexpected error:", sys.exc_info())
            return False
        return True
    
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