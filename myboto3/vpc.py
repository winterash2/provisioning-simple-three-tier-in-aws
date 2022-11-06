import sys
import botocore
import boto3

class VPC:
    '''
    Request
        CidrBlock='string',
        AmazonProvidedIpv6CidrBlock=True|False,
        Ipv6Pool='string',
        Ipv6CidrBlock='string',
        Ipv4IpamPoolId='string',
        Ipv4NetmaskLength=123,
        Ipv6IpamPoolId='string',
        Ipv6NetmaskLength=123,
        DryRun=True|False,
        InstanceTenancy='default'|'dedicated'|'host',
        Ipv6CidrBlockNetworkBorderGroup='string',
        # Tag Specifier 생략
    Response
        ec2.Vpc(id='vpc-048ea590fff96db18')
    
    Cretae VPC
        vpc = ec2_resource.create_vpc(CidrBlock='10.0.1.0/24', DryRun=True)
        #### ec2.Vpc(id='vpc-0b9e49caee88ff459')
        resource_ids['vpc']=vpc.id
    '''

    @property
    def CidrBlock(self):
        return self._CidrBlock
    
    @CidrBlock.setter
    def CidrBlock(self, value):
        self._CidrBlock = value

    # 클래스 생성 시 호출되는 초기화 함수, boto3Interfaces를 통해 미리 생성한 ec2_clinet를 전달받음
    def __init__(self, boto3Interfaces, CidrBlock = '10.0.0.0/16'):
        self._CidrBlock = CidrBlock # Boto3의 옵션과 혼동되지 않도록 네이밍을 동일하게 함
        self._ec2_resource = boto3Interfaces['ec2_resource']
        self._ec2_client = boto3Interfaces['ec2_client']
        self._id = None
    
    # VPC 생성. 옵션값을 함수 인자로 받지 않고, setter를 이용하여 설정해야 함
    def create(self):
        try:
            response = self._ec2_resource.create_vpc(
                CidrBlock = self._CidrBlock,
                # AmazonProvidedIpv6CidrBlock=True|False,
                # Ipv6Pool='string',
                # Ipv6CidrBlock='string',
                # Ipv4IpamPoolId='string',
                # Ipv4NetmaskLength=123,
                # Ipv6IpamPoolId='string',
                # Ipv6NetmaskLength=123,
                # DryRun=True|False,
                # InstanceTenancy='default'|'dedicated'|'host',
                # Ipv6CidrBlockNetworkBorderGroup='string',
                # TagSpecifications=[
                #     {
                #         'ResourceType': 'capacity-reservation'|'client-vpn-endpoint'|'customer-gateway'|'carrier-gateway'|'coip-pool'|'dedicated-host'|'dhcp-options'|'egress-only-internet-gateway'|'elastic-ip'|'elastic-gpu'|'export-image-task'|'export-instance-task'|'fleet'|'fpga-image'|'host-reservation'|'image'|'import-image-task'|'import-snapshot-task'|'instance'|'instance-event-window'|'internet-gateway'|'ipam'|'ipam-pool'|'ipam-scope'|'ipv4pool-ec2'|'ipv6pool-ec2'|'key-pair'|'launch-template'|'local-gateway'|'local-gateway-route-table'|'local-gateway-virtual-interface'|'local-gateway-virtual-interface-group'|'local-gateway-route-table-vpc-association'|'local-gateway-route-table-virtual-interface-group-association'|'natgateway'|'network-acl'|'network-interface'|'network-insights-analysis'|'network-insights-path'|'network-insights-access-scope'|'network-insights-access-scope-analysis'|'placement-group'|'prefix-list'|'replace-root-volume-task'|'reserved-instances'|'route-table'|'security-group'|'security-group-rule'|'snapshot'|'spot-fleet-request'|'spot-instances-request'|'subnet'|'subnet-cidr-reservation'|'traffic-mirror-filter'|'traffic-mirror-session'|'traffic-mirror-target'|'transit-gateway'|'transit-gateway-attachment'|'transit-gateway-connect-peer'|'transit-gateway-multicast-domain'|'transit-gateway-policy-table'|'transit-gateway-route-table'|'transit-gateway-route-table-announcement'|'volume'|'vpc'|'vpc-endpoint'|'vpc-endpoint-connection'|'vpc-endpoint-service'|'vpc-endpoint-service-permission'|'vpc-peering-connection'|'vpn-connection'|'vpn-gateway'|'vpc-flow-log'|'capacity-reservation-fleet'|'traffic-mirror-filter-rule'|'vpc-endpoint-connection-device-type'|'vpn-connection-device-type',
                #         'Tags': [
                #             {
                #                 'Key': 'string',
                #                 'Value': 'string'
                #             },
                #         ]
                #     },
                # ]
            )
            self._id = response.id
            return self._id
        except:
            print("Unexpected error:", sys.exc_info())
            return False

    def delete(self):
        if self._id == None:
            print("생성되어 있지 않은 자원입니다.")
        else:
            try:
                response = self._ec2_client.delete_vpc(
                    VpcId=self._id,
                )
                print("VPC 정상적으로 삭제하였습니다.")
                return True
            except:
                print("Unexpected error:", sys.exc_info())
                return False
        return True
    