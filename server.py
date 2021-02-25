##########################################################################
# This is a CLI application for the issuer side of the application       #
# It contains functions to help the issuer do the following:             #
# connect to an Indy pool(on Sovrin Test Network),                       #
# write schemas and credential definitions to the pool,                  #
# and issue credential offers to clients upon request.                   #
# BY: Noha Abuaesh - noha.abuaesh@gmail.com                              #
##########################################################################

from indy import pool, ledger, wallet, did, crypto, anoncreds
from indy.error import IndyError
from indy.error import PoolLedgerConfigAlreadyExistsError, DidAlreadyExistsError
from indy.error import PoolIncompatibleProtocolVersion, ErrorCode, CommonInvalidStructure
from indy.error import AnoncredsCredDefAlreadyExistsError, WalletItemNotFound
import json
import asyncio
import os, hashlib
import calendar, time, datetime

# MAIN PARAMETERS
pool_name = 'STN'
genesis_file_path = 'C:\\Users\\IEUser\\Downloads\\indy-sdk\\cli\\sovrin_genesis'
PROTOCOL_VERSION = 2

# This issuer has an endorser(Trust Anchor) DID on Sovrin network that enables it to write to the ledger
issuer = \
{
    'name': "Rehuman Account",
    'wallet_config': json.dumps({'id': 'w2'}),
    'wallet_credentials': json.dumps({'key': '12345'}),
    'seed': '1a2s3d4f5g6h7j8k9lzxcvbnm9876543',
    'did': 'N5woRhHcnE7BBh3FwsPqFJ',
    'key': '~Mt1R7BVLuLnaCjPYifJPxg',
    'schemata': [], #array to hold schemata created by this issuer
    'credential_definitions': [] #array to hold cred defs created by this issuer
}
#List of known schemata(as of now):
issuer['schemata'] = \
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
#List of known credential definitions(as of now):
issuer['credential_definitions']= \
[
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

# List of offers made by the issuer 
# It is needed to cross validate with credential requests when issuing creds
# It is a list of json objects; each looking like this: 
# {'prover_did': 'xxxx', 'offer':'xxxxxxx', 'issued_already': False}
issuer['offers'] = []

async def ready():
    await setup()
    # READY STATE: Issuer connected to pool and their wallet is active
    choice = ''
    while choice != '0':
        print("\nIssuer in Ready State. ==========================================\n")
        print("What do you want to do:")
        choice = input(
            "1. Create a new schema\n" +
            "2. Create a new credential defenition\n" +
            "3. Make a credential offer\n" +
            "4. Issue a credential\n" +
            "5. Revoke a credential\n" +
            "0. Shut down server\n\nYour choice: "
        )
    #############################################################################
        if choice == '1':           # 1. Create a new schema:
            await create_schema() 
        #############################################################################
        elif choice == '2':         # 2. Create credential defenition
            await create_credential_definiton()
        #############################################################################
        elif choice == '3':         # 3. Make a credential offer
            await make_credential_offer()
        #############################################################################
        elif choice == '4':         # 4. Issue a credential
            await issue_credential()
        #############################################################################
        elif choice == '5':         # 5. Revoke a credential
            #await revoke_credential()
            print('Not implemented yet..')
        #############################################################################
        else:
            if choice != '0':
                print("Invalid choice. Try again.")
            else:
                print("Shutting down..")
    #############################################################################
    # Close Server Application
    """print("Close and Delete wallet")
    await wallet.close_wallet(issuer['wallet'])
    await wallet.delete_wallet(wallet_config("delete", issuer['wallet_config']),
                               wallet_credentials("delete", issuer['wallet_credentials']))

    print("Close and Delete pool")
    await pool.close_pool_ledger(issuer['pool'])
    await pool.delete_pool_ledger_config(pool_name)"""
#############################################################################    
#############################################################################
async def issue_credential():
    # 1. Get credential req
    cred_req_str = input("Paste the credential request client generated here: \n")
    cred_req_object = json.loads(cred_req_str)
    # OR 
    #cred_req_object = #PASTE REQUEST HERE#
    #cred_req_str = json.dumps(cred_req_object)
    
    # 2. Retrieve matching offer
    cred_offer = find_matching_offer(cred_req_object['prover_did'], cred_req_object['cred_def_id'])
    if cred_offer == '':
        print('Sorry, cannot issue credential. A matching request was not found.')
        return
    else:
        print('Offer for this request found.')
        # 3. Prepare Credential Values 
        cred_values = await get_cred_values(json.loads(cred_offer['offer'])['schema_id'])


        print('Parameters:\n'+str(type(json.dumps(cred_offer)))+'\n'+str(type(cred_req_str))+'\n'+str(type(json.dumps(cred_values))))



        # 4. Create the credential
        credential, _, _ = \
            await anoncreds.issuer_create_credential(issuer['wallet'], json.dumps(cred_offer),
                                                    cred_req_str,
                                                    json.dumps(cred_values), None, None)

        # 5. Send Credential to client
        print('Credential issued. Please keep the following information in a safe place:')
        print(credential)
#############################################################################    
#############################################################################
async def get_cred_values(schema_id):
    schema_tuple = await get_schema(issuer['pool'], issuer['did'], schema_id)
    #Above statemnt stores a tuple that looks like this: ('schema_id_str','schema_str')
    attributes = json.loads(schema_tuple[1])['attrNames']
    # Construct cred_values json
    """ This is how credential values should look like:
        cred_values = json.dumps({
            "first_name": {"raw": "Alice", "encoded": "1139481716457488690172217916278103335"},
            "last_name": {"raw": "Garcia", "encoded": "5321642780241790123587902456789123452"},
            "degree": {"raw": "Bachelor of Science, Marketing", "encoded": "12434523576212321"},
            "status": {"raw": "graduated", "encoded": "2213454313412354"},
            "ssn": {"raw": "123-45-6789", "encoded": "3124141231422543541"},
            "year": {"raw": "2015", "encoded": "2015"},
            "average": {"raw": "5", "encoded": "5"}
        })"""
    cred_values = {}
    for a in attributes:
        raw = input('Enter the value for attribute (' + a + '): ')
        encoded = encode(raw)
        item =  {"raw": raw, "encoded": encoded}
        cred_values[a] = item

    print('Credential Values ready.\n')
    print(cred_values)

    return cred_values
#############################################################################    
############################################################################# 
def encode(val):
    # Recommended encoding trchnique of attributes:
    """ 
    -keep any 32-bit integer as is
    -for data of any other type:
        1-convert to string (string "None" for null)
        2-encode via utf-8 to bytes
        3-apply SHA-256 to digest the bytes
        4-convert the resulting digest bytes to big integer assuming sha256 output is big-endian
        5-if big integer conversion requires little endian, reverse the byte array
        6-stringify the integer as a decimal. 
    """
    val = str(val)      #1
    if val == '':       #1.2
        val = 'None'
    val.encode("utf-8") #2
    val = hashlib.sha256(val.encode()).digest() #3
    #Not sure about 5 and 6
    val = str(val)      #6
    return val
#############################################################################    
#############################################################################    
def find_matching_offer(prover_did, cred_def_id):
    # This function returns the offer sent out earlier to the giver DID
    # This helps cross validate the offer(sent earlier) with the recieved credential request
    # to ensure that only the meant DID recieves the credential

    # An entry in issuer['offers'] looks like this:
    # {'prover_did': 'xxxx', 'offer':'xxxxxxx', 'issued_already': False}

    # Find offers that have: 
        # matching prover_did AND 
        # matching cred_def_id in the offer AND 
        # NOT been issued yet (Or, check Business Rules on re-issuing lost credentials...)

    offers = list(
        filter(lambda offer: \
            (offer['prover_did'] == prover_did and \
                json.loads(offer['offer'])['cred_def_id'] == cred_def_id and \
                    bool(offer['issued_already']) == False), issuer['offers']))
    offer = ''
    if len(offers) > 1:
        print('Found multiple offers for prover (' + prover_did + '):')
        for i in range(len(offers)):
            print(str(i+1) + str(json.loads(offers[i]['offer'])['cred_def_id']))
        choice = int(input('Please enter the number for the offer that matches the request: ')) - 1
        offer = offers[choice]
    elif len(offers) == 1:
        offer = offers[0]
    elif len(offers) == 0:
        print('No matching offers found for this request.' +\
            'This could be because a credential has been alreay issued by this offer')

    return offer
#############################################################################    
#############################################################################    
async def setup():
    # 1. Create the pool if it doesn't exist
    try:
        print('\n1. Create new pool ledger configuration to connect to ledger.')
        await pool.set_protocol_version(PROTOCOL_VERSION)
        pool_config = json.dumps({'genesis_txn': genesis_file_path})
        await pool.create_pool_ledger_config(config_name=pool_name, config=pool_config)
    except PoolLedgerConfigAlreadyExistsError:
        print('Pool', pool_name, ' already exsists.')

    # 2. Connect to the pool 
    try:
        print('\n2. Open ledger and get handle')
        pool_handle = await pool.open_pool_ledger(config_name=pool_name, config=None)
        issuer['pool'] = pool_handle
    except PoolIncompatibleProtocolVersion:
        print('Error - Could not connect to pool', pool_name,
        ' due to incompatible protocol version.')
    
    # 3. Open Wallet 
    print("\n3. Create wallet\n")
    await create_wallet()

    # 4. Activate issuer account(endorser DID)
    print("\n4. Create and store DID into wallet")
    issuer['did_info'] = json.dumps({'seed': issuer['seed']})
    try:
        issuer['did'], issuer['key'] = await did.create_and_store_my_did(issuer['wallet'], issuer['did_info']) 
    except DidAlreadyExistsError:
        print("DID for ", issuer['name'], " already exists.")
#############################################################################
#############################################################################
async def create_schema():
    print("---------------------------------CREATE SCHEMA------------------------------------")
    
    # Schemata already on the ledger as of 21 FEb 21:
    # Consider making a private DB with these
    """sch = {
        "name": "Government_ID",
        "version": "0.2",
        "attrNames": ["nationality","date_of_expiry","date_of_birth","last_name","id",
                "date_of_issue","first_name","issuing_state","gender", "eye_color"]
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
    }

    sch = {
        "name": "Record_Of_Employment",
        "version": "0.2",
        "attrNames": ["first_name", "last_name", "employer", "job_title", "joining_year", "leaving_year", "reason_of_leaving", "country"]
    }
    """
    sch = await build_new_schema()

    (schema_id, schema) = \
        await anoncreds.issuer_create_schema(issuer['did'], sch['name'], sch['version'], json.dumps(sch['attrNames']))

    print("Schema Created:\nSchema ID: " + schema_id + "\n Schema: " + schema)
    issuer['schemata'].append({'id':schema_id, 'name':sch['name']})

    print("Sending new schema to Ledger...\n\n")
    schema_request = await ledger.build_schema_request(issuer['did'], schema)
    schema_request = await add_taaAccept(schema_request)
    
    if json.loads(schema_request)['op'] == "REJECT":
        print("\n\nSchema Request Rejected:\n")
        print(str(schema_request))
        print("Perhaps an identical schema already exists on the ledger")
    else:
        try:
            print(await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'], issuer['did'], schema_request))
        except CommonInvalidStructure:
            print('Ledger successfully recieved your schema request')
#############################################################################
#############################################################################
async def build_new_schema():
    print("Create a New Schema Form:")
    schema = { }
    schema['attrNames'] = read_schema_attributes()
    schema['name'] = input("Enter schema name: ")
    schema['version'] = input("Enter schema version: ")
    return schema
#############################################################################
#############################################################################
def read_schema_attributes():
    attr = []
    n = input("How many attributes in this schema?")
    for i in range(int(n)):
        attr.append(input("Enter name of attribute " + str(i+1)+": "))
    return attr
#############################################################################
#############################################################################
async def make_credential_offer():
    print("---------------------------------MAKE A CREDENTIAL OFFER TO CLIENT------------------------------")
    # 1. Choose the credential offer you want to offer the credential from
    # from the list of available credential definitions: issuer['credential definitions']
    x = 0 # variable to hold user input
    invalid_x = True
    while invalid_x:
        print("Pick the credential definition that you want to offer:")
        # Display list of available credential definitions (Can be retrieved from a Database later, but for now only 3 are available)
        for i in range(len(issuer['credential_definitions'])):
            print(str(i+1) + ': ' + issuer['credential_definitions'][i]['name'])
        x = input('Please enter any value between 1 and ' + str(len(issuer['credential_definitions'])) + ': ')
        try:
            invalid_x = int(x) < 1 or int(x) > len(issuer['credential_definitions'])
        except ValueError:
            invalid_x = True
        if invalid_x:
            print('Invalid choice. Try again.')
    
    index = int(x) -1
    cred_def_id = issuer['credential_definitions'][index]['id']
    print(cred_def_id)
    
    # 2. Prepare the offer:
    try:
        cred_offer = \
            await anoncreds.issuer_create_credential_offer(issuer['wallet'], cred_def_id)
    except WalletItemNotFound:
        print('Sorry, Couldn\'t find this credential definition "'+ cred_def_id +\
            '" in your wallet. Try creadting a new one.')
        return

    # 3. Store offer with target DID for future cross validation
    print('Credential offer ready.')
    #prover_did = input('Enter the DID of the prover for whom this offer is intended: ')
    # For testing convenience-REMOVE LATER:
    prover_did = 'UBcJYE4KfYQRtfs9iFQNSG'
    issuer['offers'].append({'prover_did': prover_did, 'offer':cred_offer, 'issued_already': False})

    # 4. Send credential offer to desired client -- HOW??? Brainstorm
    print('Send the following to the target prover:\n')
    print(cred_offer)


#############################################################################
#############################################################################
async def create_credential_definiton():
    print("---------------------------------CREATE A CREDENTIAL DEFINITION------------------------------------")
    # Choose the schema you want to create the credential defenition for
    # from the list of available schemata: issuer['schemata']
    
    x = 0 #variable to hold user input
    invalid_x = True
    while invalid_x:
        print("Pick the schema that you want to create the credential defenition for:")
        # Display list of available schemata (Can be retrieved from a Database later, but for now only 3 are available)
        for i in range(len(issuer['schemata'])):
            print(str(i+1) + ': ' + issuer['schemata'][i]['name'])
        x = input('Please enter any value between 1 and ' + str(len(issuer['schemata'])) + ': ')
        try:
            invalid_x = int(x) < 1 or int(x) > len(issuer['schemata'])
        except ValueError:
            invalid_x = True
        if invalid_x:
            print("Invalid choice. Try again.")
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
        print('credential definition created: ')
        print(cred_def)
    except AnoncredsCredDefAlreadyExistsError:
        print("A credential definition already exists in your wallet for this schema.")
        return 
    #Append to list of credential definitions(consider saving to a DB):
    try:
        issuer['credential_definitions'].append({'id':cred_def_id,'name':json.loads(cred_def)['tag']}) 
    except UnboundLocalError:
        pass

    print("3. Send new credential definition to ledger")
    cred_def_request = await ledger.build_cred_def_request(issuer['did'], cred_def)
    cred_def_request = await add_taaAccept(cred_def_request)
    try:
        print(await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'],issuer['did'], cred_def_request))
    except CommonInvalidStructure:
        print('Ledger successfully recieved your credential definition request')
#############################################################################
#############################################################################                
async def get_schema(pool_handle, _did, schema_id):
    get_schema_request = await ledger.build_get_schema_request(_did, schema_id)
    get_schema_response = await ledger.submit_request(pool_handle, get_schema_request) 

    return await ledger.parse_get_schema_response(get_schema_response)
#############################################################################
#############################################################################
async def add_taaAccept(request):

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
async def create_wallet():
    try:
        await wallet.create_wallet(wallet_config("create", issuer['wallet_config']),
                                   wallet_credentials("create", issuer['wallet_credentials']))
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    issuer['wallet'] = await wallet.open_wallet(wallet_config("open", issuer['wallet_config']),
                                                  wallet_credentials("open", issuer['wallet_credentials']))
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
    loop.run_until_complete(ready())
    loop.close()

if __name__ == '__main__':
    main()


