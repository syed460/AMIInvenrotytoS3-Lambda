# To Collect EC2 AMI Inventory into CSV file and transfer it to S3 bucket

1. First i will import the required modules
2. link the AWS services using boto3 client and get the account nubmer
3. get all the regions
4. Collect the all AMI details and iterate for reauired details and form Dictionary
5. create CSV file
6. upload the file to S3 bucket