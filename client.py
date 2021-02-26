##########################################################################
# This is a CLI application for the client side of the application       #
# It contains functions to help the client do the following:             #
# connect to an Indy pool(on Sovrin Test Network),                       #
# accept credential offers recieved from issuers,                        #
# recieve credentials and store them in their wallet,                    #
# display credentials,                                                   #
# and submit credentials for verfication                                 #
# BY: Noha Abuaesh - noha.abuaesh@gmail.com                              #
##########################################################################

from indy import pool, ledger, wallet, did, crypto, anoncreds
from indy.error import IndyError
from indy.error import PoolLedgerConfigAlreadyExistsError, DidAlreadyExistsError
from indy.error import PoolIncompatibleProtocolVersion, ErrorCode, CommonInvalidStructure
import json, asyncio

# MAIN PARAMETERS
pool_name = 'STN'
genesis_file_path = 'C:\\Users\\IEUser\\Downloads\\indy-sdk\\cli\\sovrin_genesis'
PROTOCOL_VERSION = 2

client = {
        'name': 'Applicant Account',
        'wallet_config': json.dumps({'id': 'w2'}),
        'wallet_credentials': json.dumps({'key': '12345'}),
        'seed': 'qwertyuiofzxcvbnmasd1234567890lk',
        'did': 'UBcJYE4KfYQRtfs9iFQNSG',
        'key': '~QqqyvU2P2UJaCtTockjeRJ'
    }

async def ready():
    await setup()
    # READY STATE: client connected to pool and their wallet is active
    choice = ''
    while choice != '0':
        print("Client Wallet in Ready State. ==========================================\n")
        print("What do you want to do:")
        choice = input(
            "1. Accept a credential offer\n"+
            "2. Store an issued credential to your wallet\n"+
            "3. Display all your credentials\n"+
            "4. Submit a credential to a verifier\n"+
            "0. Exit your wallet\n\nYour choice: "
        )
    #############################################################################
        if choice == '1':           # 1. Accept a Credential Offer:
            await accept_credential_offer() 
        #############################################################################
        elif choice == '2':         # 2. Store an Issued Credential to your wallet
            await store_credential()
        #############################################################################
        elif choice == '3':         # 3. Display All Your Credentials
            await display_credentials()
        #############################################################################
        elif choice == '4':         # 3. Submit a Credential to a Verifier
            await submit_credential()
        #############################################################################
        else:
            if choice != '0':
                print("Invalid choice. Try again.")
            else:
                print("Closing..")
    #############################################################################
    # Close Client Application
    print("Close and Delete wallet")
    await wallet.close_wallet(client['wallet'])
    await wallet.delete_wallet(wallet_config("delete", client['wallet_config']),
                               wallet_credentials("delete", client['wallet_credentials']))

    print("Close and Delete pool")
    await pool.close_pool_ledger(client['pool'])
    await pool.delete_pool_ledger_config(pool_name)
#############################################################################    
#############################################################################
async def accept_credential_offer():

    # 1. Get credential offer
    cred_offer_str = input("Paste the credential offer that you recieved here: \n")
    invalid_offer = True
    while invalid_offer:
        try:
            cred_offer_object = json.loads(cred_offer_str)
            invalid_offer = False
        except JSONDecodeError:
            print('Invalid offer. Try again.')
            invalid_offer = True
    # OR (For testing only)
    #cred_offer_object = PASTE OFFER HERE
    #cred_offer_str = json.dumps(cred_offer_object)

    # 2. Extract schema ID and credential definition ID from the offer
    #schema_id = cred_offer_object['schema_id']
    cred_def_id = cred_offer_object['cred_def_id']

    # 3. Create and store Master Secret in Wallet
    client['master_secret_id'] = await anoncreds.prover_create_master_secret(client['wallet'], None)
    master_secret_id = client['master_secret_id']
    print('Your master secret ID is: ')
    print(master_secret_id)
    # 4. Get Credential Definition from Ledger")
    (cred_def_id, cred_def) = \
        await get_cred_def(client['pool'], client['did'], cred_def_id)
    print('Credential definition retrieved successfully..\n')
    print(client['wallet'])
    print(client['did'])
    print(str(cred_offer_str))
    print(cred_def)

    # 5. Create Credential Request 
    (cred_request, cred_request_metadata) = \
        await anoncreds.prover_create_credential_req(client['wallet'], str(client['did']),
                                                    cred_offer_str, cred_def,
                                                    master_secret_id)

    # 6. Send Credential Request to Issuer
    print('Credential request ready. Send the following to the issuer:\n')
    print(cred_request)
#############################################################################
#############################################################################
async def get_cred_def(pool_handle, _did, cred_def_id):
    get_cred_def_request = await ledger.build_get_cred_def_request(_did, cred_def_id)
    get_cred_def_response = await ledger.submit_request(pool_handle, get_cred_def_request)
    return await ledger.parse_get_cred_def_response(get_cred_def_response)
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
        client['pool'] = pool_handle
    except PoolIncompatibleProtocolVersion:
        print('Error - Could not connect to pool', pool_name,
        ' due to incompatible protocol version.')
    
    # 3. Open Wallet 
    print("\n3. Create wallet\n")
    await create_wallet()

    # 4. Activate client account
    print("\n4. Create and store DID into wallet")
    client['did_info'] = json.dumps({'seed': client['seed']})
    try:
        client['did'], client['key'] = await did.create_and_store_my_did(client['wallet'], client['did_info']) 
    except DidAlreadyExistsError:
        print("DID for ", client['name'], " already exists.")
#############################################################################
#############################################################################   
async def create_wallet():
    try:
        await wallet.create_wallet(wallet_config("create", client['wallet_config']),
                                   wallet_credentials("create", client['wallet_credentials']))
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    client['wallet'] = await wallet.open_wallet(wallet_config("open", client['wallet_config']),
                                                  wallet_credentials("open", client['wallet_credentials']))
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

