from simpleboto3.vpc import VPC
from simpleboto3.subnet import Subnet
from simpleboto3.securitygroup import SecurityGroup


class AWSResources:
    _instance = None

    # 설정값
    _current_vpc = None # 현재 설정된 VPC(이름)

    # 이 클래스에서 관리할 AWS 자원들
    _session = None
    _vpc = None
    _subnets = {} # {id:Subnet객체} 형태로 저장하고, AWSResources.subnets['id'] 형태로 사용할 것

    @property
    def session(self):
        return self._session
    
    @property
    def vpc(self):
        return self._vpc
    
    @vpc.setter
    def vpc(self, value):
        self._vpc = value

    @property
    def subnets(self):
        return self._subnets
    
    @subnets.setter
    def subnets(self, value):
        self._subnets = value

    # __init__보다 더 먼저 수행되는 함수임. 실제로 인스턴스를 생성함
    # 싱글톤으로 사용하여 전역변수처럼 모든 곳에서 동일한 인스턴스를 사용할 수 있게끔 함
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


    # __new__보다 뒤에 실행되며, 초기화를 수행함
    # 최초 생성할때는 
    def __init__(self, session, current_vpc):
        self._session = session
        self._current_vpc = current_vpc

    def __init__(self):
        pass