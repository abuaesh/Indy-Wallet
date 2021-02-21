# This is the issuer side of the application
# The issuer connects to Indy pool, writes schemas to the pool, 
# and issues credentials upon request.
# The issuer has an endorser(Trust Anchor) DID that enables it to write to the blockchain

from indy import pool, ledger, wallet, did, crypto, anoncreds
from indy.error import IndyError
from indy.error import PoolLedgerConfigAlreadyExistsError, DidAlreadyExistsError
from indy.error import PoolIncompatibleProtocolVersion, ErrorCode, CommonInvalidStructure
from indy.error import AnoncredsCredDefAlreadyExistsError
import json
import asyncio
import os
import calendar;
import time, datetime;

# MAIN PARAMETERS
pool_name = 'STN'
genesis_file_path = 'C:\\Users\\IEUser\\Downloads\\indy-sdk\\cli\\sovrin_genesis'
PROTOCOL_VERSION = 2

async def setup_rehuman():
#############################################################################
    # 1. Create the pool if it doesn't exist
    try:
        print('\n1. Create new pool ledger configuration to connect to ledger.')
        await pool.set_protocol_version(PROTOCOL_VERSION)
        pool_config = json.dumps({'genesis_txn': genesis_file_path})
        await pool.create_pool_ledger_config(config_name=pool_name, config=pool_config)
    except PoolLedgerConfigAlreadyExistsError:
        print('Pool', pool_name, ' already exsists.')
#############################################################################    
    # 2. Connect to the pool 
    try:
        print('\n2. Open ledger and get handle')
        pool_handle = await pool.open_pool_ledger(config_name=pool_name, config=None)
    except PoolIncompatibleProtocolVersion:
        print('Error - Could not connect to pool', pool_name,
        ' due to incompatible protocol version.')
#############################################################################    
    # 3. Open Wallet 
    issuer = {
        'name': "Rehuman Account",
        'wallet_config': json.dumps({'id': 'w2'}),
        'wallet_credentials': json.dumps({'key': '12345'}),
        'pool': pool_handle,
        'seed': '1a2s3d4f5g6h7j8k9lzxcvbnm9876543',
        'did': 'N5woRhHcnE7BBh3FwsPqFJ',
        'key': '~Mt1R7BVLuLnaCjPYifJPxg',
        'schemata': [] #array holds schemata created by this issuer
    }
    print("\n3. Create wallet\n")
    await create_wallet(issuer)
#############################################################################
    # 4. Activate issuer account(endorser DID)
    print("\n4. Create and store DID into wallet")
    issuer['did_info'] = json.dumps({'seed': issuer['seed']})
    try:
        issuer['did'], issuer['key'] = await did.create_and_store_my_did(issuer['wallet'], issuer['did_info']) 
    except DidAlreadyExistsError:
        print("DID for ", issuer['name'], " already exists.")
#############################################################################
    # 5. Issuer connected and active, READY STATE
    choice = 5
    while choice != '0':
        print("\nIssuer in Ready State. ==========================================\n")
        print("What do you want to do:")
        choice = input("1. Create a new schema\n"+
            "2. Create a new credential defenition\n"+
            "3. Issue a credential\n"+
            "4. Revoke a credential\n"+
            "0. Shut down server\n\nYour choice: ")
    #############################################################################
        if choice == '1':       # 1. Create a new schema:
            print("---------------------------------CREATE SCHEMA------------------------------------")
            """sch = {
                "name": "Government_ID",
                "version": "0.1",
                "attrNames": ["nationality","date_of_expiry","date_of_birth","last_name","id",
                        "date_of_issue","first_name","issuing_state","gender"]
            }

            sch = {
                "name": "Eduaction_Certificate",
                "version": "0.1",
                "attrNames": ["first_name", "last_name", "institution", "degree", "gpa", "major", "minor", "graduation_date"]
            }
            
            sch = {
                "name": "Record_Of_Employment",
                "version": "0.1",
                "attrNames": ["first_name", "last_name", "employer", "job_title", "joining_year", "leaving_year", "reason_of_leaving"]
            }"""

            sch = {
                "name": "Record_Of_Employment",
                "version": "0.2",
                "attrNames": ["first_name", "last_name", "employer", "job_title", "joining_year", "leaving_year", "reason_of_leaving", "country"]
            }

            (schema_id, schema) = \
                await anoncreds.issuer_create_schema(issuer['did'], sch['name'], sch['version'], json.dumps(sch['attrNames']))

            print("Schema Created:\nSchema ID: " + schema_id + "\n Schema: " + schema)
            issuer['schemata'].append({schema_id, schema})

            print("Sending new schema to Ledger...\n\n")
            schema_request = await ledger.build_schema_request(issuer['did'], schema)
            schema_request = await add_taaAccept(schema_request, issuer)
            
            if schema_request['op'] == "REJECT":
                print("\n\nSchema Request Rejected:\n")
                print(str(schema_request))
                print("Perhaps an identical schema already exists on the ledger")
            else:
                try:
                    print(await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'], issuer['did'], schema_request))
                except CommonInvalidStructure:
                    print('Ledger successfully recieved your schema request')
    #############################################################################
        elif choice == '2':       # 2. Create credential defenition
            print("---------------------------------CREATE A CREDENTIAL DEFINITION------------------------------------")
            # Choose the schema you want to create the credential defenition for
            # from the following list of available schemata:
            issuer['schemata'] = 
            [
                {
                    'id': 'N5woRhHcnE7BBh3FwsPqFJ:2:Government_ID:0.1',
                    'name': 'Government ID'
                },
                {
                    'id': 'N5woRhHcnE7BBh3FwsPqFJ:2:Eduaction_Certificate:0.1',
                    'name': 'Educational Certificate'
                },
                {
                    'id': 'N5woRhHcnE7BBh3FwsPqFJ:2:Record_Of_Employment:0.1',
                    'name': 'Record of Employment'
                }
            ]
            x = 0 #variable to hold user input
            
            while int(x) < 1 or int(x) > len(issuer['schemata']):
                print("Pick the schema that you want to create the credential defenition for:")
                # Display list of available schemata (Can be retrieved from a Database later, but for now only 3 are available)
                for i in range(len(issuer['schemata'])):
                    print(str(i+1) + ': ' + issuer['schemata'][i]['name'])
                x = input('Please enter any value between 1 and ' + str(len(issuer['schemata'])) + ': ')
            
            index = int(x) -1
            schema_id = issuer['schemata'][index]['id']

            print('1. Get Schema from Ledger')
            
            (schema_id, sch) = \
                await get_schema(issuer['pool'], issuer['did'], schema_id)

            issuer['schemata'][index]['schema'] = sch
            print('Schema retrieved: ')
            print(sch)
            print("2. Create and store in Wallet (" + issuer['schemata'][index]['name'] + ") Credential Definition..")

            name = input("Give a name to this credential definition: ")
            revoc = input("Do you want credentials issued for this definition to support revocation? (y/n)")
            revoc = revoc.lower()
            if revoc == 'y':
                revoc = True
            else:
                revoc = False

            cred_def = {
                'tag': name,
                'type': 'CL',
                'config': {"support_revocation": revoc}
            }
            try:
                (cred_def_id, cred_def) = \
                    await anoncreds.issuer_create_and_store_credential_def(issuer['wallet'], issuer['did'],
                                                                    sch, cred_def['tag'],
                                                                    cred_def['type'],
                                                                    json.dumps(cred_def['config']))
                print('credential definition id: ')
                print(cred_def_id)
            except AnoncredsCredDefAlreadyExistsError:
                print("A credential definition already exists in your wallet for this schema.")
            #Append to list of credential definitions(consider saving to a DB):
            #issuer['credential_definitions'].append({'id':cred_def_id,'name':cred_def['tag']}) 

            print("3. Send new credential definition to ledger")
            cred_def_request = await ledger.build_cred_def_request(issuer['did'], cred_def)
            cred_def_request = await add_taaAccept(cred_def_request, issuer)
            try:
                print(await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'],issuer['did'], cred_def_request))
            except CommonInvalidStructure:
                print('Ledger successfully recieved your credential definition request')
    #############################################################################
        #List of known credential definitions(for now)
        issuer['credential_definitions']= [
                        {
                            'id': 'N5woRhHcnE7BBh3FwsPqFJ:3:CL:188415:GovIDCredDef',
                            'name': 'Government ID'
                        },
                        {
                            'id': 'N5woRhHcnE7BBh3FwsPqFJ:3:CL:188416:edu_cert_cred_def',
                            'name': 'Educational Certificate'
                        },
                        {
                            'id': 'N5woRhHcnE7BBh3FwsPqFJ:3:CL:188417:Record_of_employment',
                            'name': 'Record of Employment'
                        }
                        ]
#############################################################################
#############################################################################
    
#############################################################################
async def get_schema(pool_handle, _did, schema_id):
    get_schema_request = await ledger.build_get_schema_request(_did, schema_id)
    get_schema_response = await ledger.submit_request(pool_handle, get_schema_request) 

    return await ledger.parse_get_schema_response(get_schema_response)
#############################################################################
async def add_taaAccept(request, issuer):

    print("---------------------------------TAA PROCEDURE------------------------------------")

    # 1. Get Latest TAA from ledger
    taa_request = await ledger.build_get_txn_author_agreement_request(issuer['did'], None)
    latest_taa = await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'], issuer['did'], taa_request)
    print("Step A - TAA Retrieved ")
    #print(latest_taa)

    # 2. Get Acceptance Mechanisms List(AML)
    acceptance_mechanism_request = await ledger.build_get_acceptance_mechanisms_request(issuer['did'], None, None)
    aml = await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'], issuer['did'], acceptance_mechanism_request)
    print("Step B - AML Retrieved ")
    #print(json.loads(aml)['result']['data']['aml'])
    
    # 3. Append acceptance to your request
    latest_taa = json.loads(latest_taa)
    taa_digest = latest_taa['result']['data']['digest']
    #d = datetime.datetime.now()
    #timestamp = time.mktime(d.timetuple())
    aml = json.loads(aml)
    timestamp = aml['result']['txnTime']
    timestamp = int (timestamp/(60*60*24)) #Need to set timestamp to beginning of the day to reduce corratability risk
    timestamp = timestamp*60*60*24 #return back to POSIX timestamp
    #print (timestamp)

    # Values for Txn Author Agreement acceptance mechanism is one of:
    # ['at_submission', 'click_agreement', 'for_session', 'on_file', 'product_eula', 'service_agreement', 'wallet_agreement']
    request = await ledger.append_txn_author_agreement_acceptance_to_request(request, None, None, taa_digest, 'at_submission', timestamp)
    request = await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'], issuer['did'], request)

    print("Step C - TAA Appended to your Request ")
    #print(request)
    print("COMPLETED TAA PROCEDURE------------------------------------")
    # 4. Return appended request
    return request
#############################################################################
#############################################################################
async def create_wallet(identity):
    try:
        await wallet.create_wallet(wallet_config("create", identity['wallet_config']),
                                   wallet_credentials("create", identity['wallet_credentials']))
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    identity['wallet'] = await wallet.open_wallet(wallet_config("open", identity['wallet_config']),
                                                  wallet_credentials("open", identity['wallet_credentials']))
#############################################################################
#############################################################################
def wallet_config(operation, wallet_config_str):
    wallet_config_json = json.loads(wallet_config_str)

    # print(operation, json.dumps(wallet_config_json))
    return json.dumps(wallet_config_json)
#############################################################################
#############################################################################
def wallet_credentials(operation, wallet_credentials_str):
    wallet_credentials_json = json.loads(wallet_credentials_str)
    return json.dumps(wallet_credentials_json)
#############################################################################
#############################################################################
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_rehuman())
    loop.close()

if __name__ == '__main__':
    main()


