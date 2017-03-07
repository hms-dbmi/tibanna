# -*- coding: utf-8 -*-
# from core import utils
# import boto3
from core.orc_utils import orc_init_and_connect, orc_run_job

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# check the status and other details of import
def handler(event, context):
    '''
    this is to run the actual task
    '''

    client, username, password = orc_init_and_connect()
    logging.info("client, username, password")
    logging.info(client, username, password)

    # command:
    ret_id = orc_run_job(client, '"bash ./hackathon_align.sh"', 'short',
                         '2:00',
                         extras='-R "rusage[mem=5000] rusage[tmp=10000]" -o hackathon_align.lsf')
    logging.info('ALIGNING ID: %s' % ret_id)
    return {'runid': ret_id}
