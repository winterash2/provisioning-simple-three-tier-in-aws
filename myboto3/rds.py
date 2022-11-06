import sys
import botocore
import boto3
import time

class RDS:
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value

    def __init__(self, boto3Interfaces, Vpc, DBName, Subnets, SecurityGroups, DBEngine, Version):
        self._Vpc = Vpc
        self._rds_client = boto3Interfaces['rds_client']
        self._Tags = []
        self._name = DBName

        # DB 서브넷 그룹 생성
        _subnetIds = []
        for subnet in Subnets:
            _subnetIds.append(subnet.id)
        _securityGroupIds = []
        for sg in SecurityGroups:
            _securityGroupIds.append(sg.id)

        response = self._rds_client.create_db_subnet_group(
            DBSubnetGroupName = DBName+'_subnet_group',
            DBSubnetGroupDescription = DBName+'_subnet_group',
            SubnetIds = _subnetIds
        )

        # DB 인스턴스 생성
        rds_instances = self._rds_client.create_db_instance(
            DBName = self._name,
            DBInstanceIdentifier = self._name + 'instance',
            AllocatedStorage=10,
            DBInstanceClass='db.t2.micro', # DB 인스턴스 사양
            Engine = DBEngine, # DB 엔진
            MasterUsername='root', # master user name
            MasterUserPassword='password', # master user password
            VpcSecurityGroupIds = _securityGroupIds,
            # AvailabilityZone='ap-northeast-2a', Multi AZ 옵션일 때는 AZ 지정 불가
            DBSubnetGroupName = DBName+'_subnet_group', # DB 서브넷 그룹 지정
            Port=3306, # DB Port
            MultiAZ=True, # 다중 AZ 구성
            EngineVersion = Version, # Engine Version
            PubliclyAccessible=False, # 외부 접속 여부
        )
        print("RDS 생성 중입니다. 3분가량 소요됩니다.")
        time.sleep(300)
        
        rds_instance = self._rds_client.describe_db_instances(DBInstanceIdentifier='rdsInstances')
        self._endPoint = rds_instance['DBInstances'][0].get('Endpoint').get('Address')
        
        print("RDS DB Endpoint IP=", self._endPoint, ", Port= 3306")

    def delete(self):
        response = self._rds_client.delete_db_instance(
            DBInstanceIdentifier = self._name + 'instance',
            SkipFinalSnapshot=True,
            DeleteAutomatedBackups=False
        )

# SubnetIds, DBName, DBInstanceIdentifier=DBName+'instance', VpcSecurityGroupIds, DBSubnetGroupName