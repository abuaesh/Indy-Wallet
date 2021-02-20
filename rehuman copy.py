# This is the issuer side of the application
# The issuer connects to Indy pool, writes schemas to the pool, 
# and issues credentials upon request.
# The issuer has an endorser(Trust Anchor) DID that enables it to write to the blockchain

from indy import pool, ledger, wallet, did, crypto, anoncreds
from indy.error import IndyError
from indy.error import PoolLedgerConfigAlreadyExistsError, DidAlreadyExistsError
from indy.error import PoolIncompatibleProtocolVersion, ErrorCode
import json
import asyncio
import os

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
    print("\nIssuer in Ready State. \n")
    print("What do you want to do:")
    # Make it a while loop:
    choice = input("1. Create a new schema\n"+
        "2. Issue a new credential\n"+
        "3. Revoke a credential\n")
#############################################################################
    if choice == '1':
        sch = await create_schema()
        (schema_id, schema) = \
        await anoncreds.issuer_create_schema(issuer['did'], sch['name'], sch['version'],
                                             json.dumps(sch['attrNames']))

        print("Schema Created:\nSchema ID: " + schema_id + "\n Schema: " + schema)
        issuer['schemata'].append({schema_id, schema})

        print("Sending new schema to Ledger")
        await send_schema(issuer['pool'], issuer['wallet'], issuer['did'], schema)
#############################################################################
#############################################################################
async def send_schema(pool_handle, wallet_handle, _did, schema):
    schema_request = await ledger.build_schema_request(_did, schema)
    print("\n\nSchema Request:\n")
    print(str(schema_request)+"\n\n")
    print(await ledger.sign_and_submit_request(pool_handle, wallet_handle, _did, schema_request))
#############################################################################
#############################################################################
async def create_schema():
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


