#! /usr/bin/env python

import os
import shutil
import zipfile

import boto3

from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

if os.path.exists("coinpan.zip"):
    print("coinpan.zip already Exists. Move to old.")
    shutil.move("coinpan.zip", "coinpan.zip.old")

with zipfile.ZipFile("coinpan.zip", "w") as zf:
    print("Including Packages...")
    zip_root = ".lambdaenv/lib/python3.6/site-packages/"
    for root, dirs, files in os.walk(zip_root):
        for f in files:
            zf.write(os.path.join(root, f), os.path.join(root, f).replace(zip_root, ""))
    print("Including Python File...")
    zf.write("coinpan.py")
print("ZIP Done. Upload to S3...")

s3 = boto3.client("s3", region_name="ap-northeast-2",
                  aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3.upload_file("coinpan.zip", "ulismoon", "coinpan.zip")
print("S3 Uploaded. Change Lambda to new archive...")
lm = boto3.client("lambda", region_name="ap-northeast-2",
                  aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
resp = lm.update_function_code(FunctionName="coinpanSpreadAlimi", S3Bucket="ulismoon", S3Key="coinpan.zip")
print(resp)
print("All Done")
