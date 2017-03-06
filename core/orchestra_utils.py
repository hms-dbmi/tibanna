from __future__ import print_function

import json
import datetime
import boto3
import os
import requests
import random
import mimetypes
import paramiko
import utils
from uuid import uuid4
from zipfile import ZipFile
from io import BytesIO

from wranglertools import fdnDCIC

def first_run():
    client = paramiko.SSHClient()
    # lazy option, automatically add missing host keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client_username = utils.get_key('orc_user')
    client_pass = utils.get_key('orc_pass')
    client.connect('orchestra.med.harvard.edu', username=client_username, password=client_pass)
    stdin, stdout, stderr = client.exec_command('bsub -q short -W 2:00 -o hackathon.lsf "bash ./hackathon_tib.sh"')
    try:
        job_id = extract_job_id(stdout)
        print('BSUB ID:', job_id)
    except ValueError:
        print('Orchestra job not succesfully submitted')
        return


def extract_job_id(stdout):
    """
    Take stdout from a submitted bsub orchestra command and return the job id
    as a string. Raise ValueError if stdout doesn't contain the id.
    Example format: u'Job <3189828> is submitted to queue <short>.'
    """
    l = stdout.readlines()
    if len(l) != 1 or 'submitted' not in l[0]:
        raise ValueError
    s_idx = l[0].find('<')
    e_idx = l[0].find('>')
    if s_idx == -1 or e_idx == -1:
        raise ValueError
    return l[0][s_idx+1:e_idx]



if __name__ == "__main__":
    first_run()
