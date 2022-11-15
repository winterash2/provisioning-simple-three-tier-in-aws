

def ec2_create_tag(simpleBoto3, resource, key, value):
    try:
        response = simpleBoto3.ec2_client.create_tags(
            Resources=[
                resource.id,
            ],
            Tags=[
                {
                    'Key': key,
                    'Value': value
                },
            ]
        )
    except Exception as err:
        print("Tag 생성 중 알 수 없는 에러가 발생하였습니다.", str(err))
        raise
    return True