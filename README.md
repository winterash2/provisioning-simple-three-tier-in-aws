# provisioning-simple-three-tier-in-aws

Boto3를 이용해 3-Tier 아키텍처를 구성하는 Python 코드입니다.

---
##  프로그램 사용 방법

이 프로그램은 Python으로 작성되어있으며 AWS의 Boto3 라이브러리를 사용합니다. 아래와 같이 Python과 Boto3를 설치해주시기 바랍니다.

### 필요 패키지 설치
```
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt install python3.7
$ sudo apt-get install python3-venv
$ pip install boto3
```

### 모듈 설치
이 프로그램 위치에서 python 가상환경을 만들고 프로그램을 실행하기 위한 python 모듈을 아래와 같이 설치합니다.
```
$ cd $PROGRAM_HOME
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### 설정
프로그램을 실행하기 전 config.yaml 파일의 내용을 채워주시기 바랍니다.
- `ACCESS_KEY`: AWS ACCESS KEY
- `SECRET_KEY`: AWS SECRET KEY
- `AWS_REGION_NAME`: AWS 리전
- `KEYPAIR_NAME`: 사용할 키 페어 이름(기존에 있을 시 지정 가능, 없을 시 새로 생성)
- `MySQLVersion`: MySQL 버전(8.0.23, 8.0.25, 8.0.26, 8.0.27, 8.0.28, 8.0.30 중 선택 가능)
```
## AWS 자격증명
ACCESS_KEY: AAAAAAAAAAAAAAAAAAAA
SECRET_KEY: CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
AWS_REGION_NAME: ap-northeast-2

## 키페어 이름
KEYPAIR_NAME: defaultKeyPair

## RDS
### 사용 가능한 MySQL 버전은 8.0.23, 8.0.25, 8.0.26, 8.0.27, 8.0.28, 8.0.30 입니다.
### 이 중 하나를 선택하여 입력해주시기 바랍니다.
MySQLVersion: 8.0.23 
```

### 프로그램 실행
프로그램을 실행합니다.
```
$ python provisioningSimpleThreeTierInAws.py
```

### 종료
실행을 마치고 난 후 python 가상환경을 종료해줍니다.
```
$ deactivate
```

