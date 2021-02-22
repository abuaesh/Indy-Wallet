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
import json

# MAIN PARAMETERS
pool_name = 'STN'
genesis_file_path = 'C:\\Users\\IEUser\\Downloads\\indy-sdk\\cli\\sovrin_genesis'
PROTOCOL_VERSION = 2

client = {
        'name': 'Applicant Account',
        'wallet_config': json.dumps({'id': 'w2'}),
        'wallet_credentials': json.dumps({'key': '12345'}),
    }

async def ready():
    await setup()
    # READY STATE: client connected to pool and their wallet is active
    choice = ''
    while choice != '0':
        print("\Client Wallet in Ready State. ==========================================\n")
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
            await accept_credential() 
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
            print("Invalid choice. Try again.")
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
    await create_wallet(alice)
    (alice['did'], alice['key']) = await did.create_and_store_my_did(alice['wallet'], "{}")