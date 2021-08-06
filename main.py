#!/bin/python3

import json, csv
import boto3
from pprint import pprint
from datetime import datetime
import subprocess, os

#def lambda_handler(event, context):
print("---------------Script Starts-------------")
print("")

#-------------------Variable-------------

Bucket_region = os.getenv("Bucket_region")
Bucket_Name = os.getenv("Bucket_Name")
filename= os.getenv("filename")

#----------------------------------------
#defining file name
def date_on_filename(filename, file_extension):  
	date = str(datetime.now().date())
	return filename + "-" + date + "." + file_extension

report_filename = date_on_filename(filename, "csv")
print(f"output file name: {report_filename}")

#file path
filepath= "/tmp/" + report_filename
print(f"Output File Patch {filepath}")
print("")

#Collecting Account Number using any region
sts_cli=boto3.client(service_name='sts', region_name="us-east-1")
responce_1=sts_cli.get_caller_identity()
account_number=responce_1.get("Account")
#--------------------------------------------

#--------------Manually update the dic.keys() to header_list if mismatch

header_list=['Region', 'OwnerID', 'Name', 'WBS', 'AIM Name', 'Description', 'AIM ID', 'Status', 'CreatedTime', 'Platform', \
    'Architecture', 'SnapshotId', 'DeviceName', 'VolumeType', 'VolumeSize', 'Encrypted', 'DeleteOnTermination', 'Root Device Type', \
        'RootDeviceName', 'Public', 'EnaSupport', 'Hypervisor', 'ImageLocation', 'ImageType', 'ProductCodes', \
            'UsageOperation', 'VirtualizationType', 'SriovNetSupport']
print(f"Header for CSV file = {header_list}")
print(" ")
# to add 50 Tag headers
for v in range(1,51):
    header_list.append(f'Tag{v}')
#--------------------------------------------
    #Collect all regions if needed
#--------------------------------------------
#-----------collect all region list into Regions
print("collecting all the regions name")

ec2_cli = boto3.client(service_name='ec2', region_name="us-east-1")    
responce=ec2_cli.describe_regions()
#pprint(responce['Regions'])
Regions=[]
for each in responce['Regions']:
    #print(each['RegionName'])
    Regions.append(each['RegionName'])    
print(f"Total {len(Regions)} regions")
print("")

#Regions=['us-west-2']
x=1 

#----------creating file with headder
print("Oppening the csv file to append each server details")
with open(filepath,'w') as csv_file:
#with open("outpu.csv",'w') as csv_file:
    Writer=csv.writer(csv_file)
    Writer.writerow(header_list)

    
    print("Now going through each regions to check ec2 details")
    print("")
    for region in Regions:
        #print(region)
        #print(type(region))
        ec2_cli=boto3.client(service_name='ec2', region_name=region)
        #describe_images
        all_AMI=ec2_cli.describe_images(Owners=[account_number,],)
        #pprint(all_snapshots)
        #print(" ")
        for each in all_AMI['Images']:
            dic={'Region':region,'OwnerID':account_number,'Name': 'NA','WBS':'NA','AIM Name': 'NA','Description':'NA','AIM ID':'NA','Status':'NA',
            'CreatedTime':'NA','Platform':'NA','Architecture':'NA','SnapshotId':['NA'],'DeviceName':['NA'],'VolumeType':['NA'],'VolumeSize':['NA'],
            'Encrypted':['NA'],'DeleteOnTermination':['NA'],'Root Device Type':'NA','RootDeviceName':'NA','Public':'NA',
            'EnaSupport':'NA','Hypervisor':'NA','ImageLocation':'NA','ImageType':'NA','ProductCodes':['NA'],'UsageOperation':'NA',
            'VirtualizationType':'NA','SriovNetSupport':'NA'}
            #pprint(each)
            if each.get('Tags') != None:
                for tags in each['Tags']:
                    #print(tags.values())
                    if tags['Key'] == 'Name':
                        #print("Yes, found Name-Tag")
                        #print(tags['Value'])
                        dic['Name']=tags['Value']
                    if tags['Key'] == 'WBS':
                        #print("Yes, found WBS-Tag")
                        dic['WBS']=tags['Value']
                b=1
                for tag in each['Tags']:
                    #print(each.values())
                    dic[f'Tag{b}']=list(tag.values())
                    b+=1
            if each.get('Name') != None:
                dic['AIM Name']=each['Name']
            if each.get('Description') != None:
                dic['Description']=each['Description']
            dic['AIM ID']=each['ImageId']
            dic['Status']=each['State']
            #print(each['CreationDate'].strftime("%m/%d/%Y, %H:%M:%S"))
            CreateTime=datetime.strptime(each['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z")
            CreateTime.strftime("%m/%d/%Y, %H:%M:%S")
            dic['CreatedTime']=CreateTime.strftime("%m/%d/%Y, %H:%M:%S")
            if each.get('PlatformDetails') != None:
                dic['Platform']=each['PlatformDetails']
            dic['Architecture']=each['Architecture']
            #pprint(each['BlockDeviceMappings'])
            DeviceName=[]
            snapshotid=[]
            VolumeType=[]
            VolumeSize=[]
            Encrypted=[]
            DeleteOnTermination=[]
            for block in each['BlockDeviceMappings']:
                snapshotid.append(block['Ebs']['SnapshotId'])
                DeviceName.append(block['DeviceName'])
                VolumeType.append(block['Ebs']['VolumeType'])
                VolumeSize.append(block['Ebs']['VolumeSize'])
                Encrypted.append(block['Ebs']['Encrypted'])
                DeleteOnTermination.append(block['Ebs']['DeleteOnTermination'])

            dic['DeviceName']=DeviceName
            dic['SnapshotId']=snapshotid
            dic['VolumeType']=VolumeType
            dic['VolumeSize']=VolumeSize
            dic['Encrypted']=Encrypted
            dic['DeleteOnTermination']=DeleteOnTermination
            dic['Root Device Type']=each['RootDeviceType']
            
            dic['Public']=each['Public']
            if each.get('EnaSupport') != None:
                dic['EnaSupport']=each['EnaSupport']
            if each.get('Hypervisor') != None:
                dic['Hypervisor']=each['Hypervisor']
            if each.get('ImageLocation') != None:
                dic['ImageLocation']=each['ImageLocation']
            if each.get('ImageType') != None:
                dic['ImageType']=each['ImageType']
            if each.get('ProductCodes') != None:
                ProductCodes=each['ProductCodes']
                print(ProductCodes)
                dic['ProductCodes']=ProductCodes
            

            dic['RootDeviceName']=each['RootDeviceName']
            if each.get('UsageOperation') != None:
                dic['UsageOperation']=each['UsageOperation']
            if each.get('UsageOperation') != None:
                dic['VirtualizationType']=each['VirtualizationType']
            if each.get('SriovNetSupport') != None:
                dic['SriovNetSupport']=each['SriovNetSupport']
            



            print(dic.keys())
            Writer.writerow(dic.values())
            print(f"\n------AMI {x} details been taken\n")
            x+=1

#to check the what are the files exist under folder
#lscommand = subprocess.run(f"ls {filepath}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
lscommand = subprocess.run(f"ls {filepath}", shell=True, capture_output=True, text=True)
print(f"Output file Location:\n{lscommand.stdout}")



#transfer the file to s3
print(f"moving the file to S3 Bucket: {Bucket_Name}")
s3_cli=boto3.client(service_name='s3', region_name=Bucket_region)
#s3_cli.upload_file(filepath, Bucket_Name, report_filename)

#remove the file from container
#removefile=subprocess.run(f"rm -rfv {filepath}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#print(f"Removed the output file from /tmp/ dir\n{removefile.stdout.decode('utf-8')}")
print(" ")
print("-----------------Script Ends--------------------")
