import base64
import json
import logging

from boto3 import Session
from botocore.exceptions import ClientError

cloud_logger = logging.getLogger("cloud")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
cloud_logger.addHandler(handler)
cloud_logger.setLevel(logging.INFO)


class SecretsManager:
    @staticmethod
    def get_secret(secret_name, region_name="eu-west-1", deploy='prod'):
        if deploy == 'dev':
            with open('creds.json') as json_file:
                creds = json.load(json_file)
            access_id = creds['id']
            access_key = creds['key']
            session = Session(aws_access_key_id=access_id, aws_secret_access_key=access_key)
        else:
            session = Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise e
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return secret
