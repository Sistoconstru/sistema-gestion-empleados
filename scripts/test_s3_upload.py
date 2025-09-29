import boto3
import os

BUCKET = os.environ.get('AWS_STORAGE_BUCKET_NAME')
REGION = os.environ.get('AWS_S3_REGION_NAME', 'sa-east-1')
ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Archivo de prueba
TEST_FILE = 'test_s3.txt'
TEST_KEY = 'test_s3_upload/test_s3.txt'

# Crear archivo de prueba
with open(TEST_FILE, 'w') as f:
    f.write('Prueba de subida a S3 desde Railway')

# Crear cliente S3
s3 = boto3.client(
    's3',
    region_name=REGION,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

try:
    s3.upload_file(TEST_FILE, BUCKET, TEST_KEY)
    print(f'Archivo subido exitosamente a s3://{BUCKET}/{TEST_KEY}')
except Exception as e:
    print(f'Error subiendo archivo a S3: {e}')
