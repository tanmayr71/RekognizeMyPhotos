import logging
import base64
import json
import boto3
import os
import time
import requests
import math
import dateutil.parser
import datetime



ES_URL = "https://search-myphotos1-7aduclkckt6r6ayol6deekjtny.us-east-1.es.amazonaws.com"
ES_USER = 'Master'
ES_PASS = 'Master@123'