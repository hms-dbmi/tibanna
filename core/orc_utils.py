from __future__ import print_function

import time
import paramiko
import utils


"""
Functions to add (?)

orc_to_s3: use a .sh with a virtualenv with boto3? or scp somehow?
    see utils.s3_put for inspiration

build_venv: create a virtual environment corresponding to requirements.txt

build_sh: some function to generate .sh from list to run? Could have defaults:
    like <#!/bin/bash>
"""

def test_fxn():
    """
    Test function. Runs part of an alignment on orchestra
    """
    client, username, password = orc_init_and_connect()
    stdin, stdout, stderr = client.exec_command('source hackathon_venv/bin/activate')
    # command:
    ret_id = orc_run_job(client, '"bash ./hackathon_align.sh"', 'short',
         '2:00', extras='-R "rusage[mem=5000] rusage[tmp=10000]" -o hackathon_align.lsf')
    print('ALIGNING')
    print('ID:', ret_id)
    sleep_amt = 5
    job_status = 'START'
    while job_status not in ['DONE', 'EXIT']:
        time.sleep(sleep_amt)
        sleep_amt = sleep_amt*2
        job_status = orc_job_status(client, ret_id)
        print('ID:', ret_id, 'STATUS:', job_status)
    # aws s3 cp ./hackathon_bam/hackathon_sample_data-sort.bam s3://carlv
    ret_id = orc_run_job((client, 'aws s3 cp ./hackathon_bam/hackathon_sample_data-sort.bam s3://carlv', 'short','2:00')
    print('COPYING RESULTS TO S3')
    print('ID:', ret_id)
    sleep_amt = 5
    job_status = 'START'
    while job_status not in ['DONE', 'EXIT']:
        time.sleep(sleep_amt)
        sleep_amt = sleep_amt*2
        job_status = orc_job_status(client, ret_id)
        print('ID:', ret_id, 'STATUS:', job_status)

def orc_init_and_connect():
    """
    SSH into orchestra using username and password stored in S3
    This relies on having correct S3 env variables in place.
    Returns a connected paramiko client.
    """
    client = paramiko.SSHClient()
    # lazy option, automatically add missing host keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client_username = utils.get_key('orc_user')
    client_password = utils.get_key('orc_pass')
    client.connect('orchestra.med.harvard.edu', username=client_username, password=client_password)
    return client, client_username, client_password


def orc_run_job(client, command, queue, time_limit, extras=''):
    """
    Use an initialized paramiko client to run an orchestra bsub job.
    Required params are string orchestra command, string queue (short, long,
    mcore...), string time_limit (formatted as hrs:mins), and any extra string
    params to run.
    Returns job_id of the submitted job

    command arg may be an .sh to run or a different linux command
    """
    bsub = 'bsub -q ' + queue + ' -W ' + time_limit + ' ' + extras + ' ' + command
    stdin, stdout, stderr = client.exec_command(bsub)
    try:
        job_id = extract_job_id(stdout)
    except ValueError:
        print('Orchestra job not succesfully submitted')
        return
    return job_id


def orc_job_status(client, job_id):
    """
    Use the paramiko client and job_id to get the status of a bsub job.
    Statuses are: PEND, RUN, DONE, EXIT (on error), and SSUSP
    """
    stdin, stdout, stderr = client.exec_command('bjobs -l ' + job_id)
    strip_lines = [line.strip() for line in stdout.readlines()]
    lines = ''.join(strip_lines)
    for line in lines.split(','):
        if 'Status' in line:
            s_idx = line.find('<')
            e_idx = line.find('>')
            if s_idx == -1 or e_idx == -1:
                continue
            return line[s_idx+1:e_idx]
    return 'UNKNOWN'


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
    test_fxn()
