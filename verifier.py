##########################################################################
# This is a CLI application for the verifier side of the application     #
# It contains functions to help the verifier do the following:           #
# connect to an Indy pool(on Sovrin Test Network),                       #
# accept credentials from provers,                                       #
# test their truthfulness against,                                       #
# display display whether or not these credentials are accepted,         #
# BY: Noha Abuaesh - noha.abuaesh@gmail.com                              #
##########################################################################

from indy import pool, ledger, wallet, did, crypto, anoncreds
from indy.error import IndyError
from indy.error import PoolLedgerConfigAlreadyExistsError, DidAlreadyExistsError
from indy.error import PoolIncompatibleProtocolVersion, ErrorCode, CommonInvalidStructure
from json.decoder import JSONDecodeError
import json, asyncio

# MAIN PARAMETERS
pool_name = 'STN'
genesis_file_path = 'C:\\Users\\IEUser\\Downloads\\indy-sdk\\cli\\sovrin_genesis'
PROTOCOL_VERSION = 2

verifier = {
        'name': 'Verifier Account',
        'wallet_config': json.dumps({'id': 'w3'}),
        'wallet_credentials': json.dumps({'key': '12345'}),
        #'seed': 'qwertyuiofzxcvbnmasd1234567890lk',
        'did': 'NY2d22ZknDAqgTfnsc4MGr',
        'key': '~TPYn2iq6ubiHqT294377Tr'
    }
#############################################################################
async def ready():
    await setup()
    # READY STATE: verifier connected to pool and their wallet is active
    choice = ''
    while choice != '0':
        print("Verifier in Ready State. ==========================================\n")
#############################################################################
#############################################################################
async def get_cred_def(pool_handle, _did, cred_def_id):
    get_cred_def_request = await ledger.build_get_cred_def_request(_did, cred_def_id)
    get_cred_def_response = await ledger.submit_request(pool_handle, get_cred_def_request)
    return await ledger.parse_get_cred_def_response(get_cred_def_response)