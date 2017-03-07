# -*- coding: utf-8 -*-
from core.orc_utils import orc_init_and_connect, orc_job_status

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# check the status and other details of import
def handler(event, context):
    '''
    this is to check if the task run is done:
    http://docs.sevenbridges.com/reference#get-task-execution-details
    '''
    # connect
    client, username, password = orc_init_and_connect()
    logging.info("client, username, password")
    logging.info(client, username, password)

    job_id = event.get('runid')

    # check status of workflow, error if not done
    status = orc_job_status(client, job_id)
    if status not in ['DONE', 'EXITED']:
        data = {'runid': job_id,
                'status': status}
        raise Exception('Task not finished => %s' % data)

    return {'runid': job_id,
            'run_response': status
            }
