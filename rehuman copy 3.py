# This is the issuer side of the application
# The issuer connects to Indy pool, writes schemas to the pool, 
# and issues credentials upon request.
# The issuer has an endorser(Trust Anchor) DID that enables it to write to the blockchain

from indy import pool, ledger, wallet, did, crypto, anoncreds
from indy.error import IndyError
from indy.error import PoolLedgerConfigAlreadyExistsError, WalletAlreadyExistsError, DidAlreadyExistsError
from indy.error import PoolIncompatibleProtocolVersion, ErrorCode
import json
import asyncio
import os

# MAIN PARAMETERS
genesis_file_path = 'C:\\Users\\IEUser\\Downloads\\indy-sdk\\cli\\sovrin_genesis'

async def setup_rehuman():
#############################################################################
    # 1. Create the pool if it doesn't exist
    try:
        await pool.set_protocol_version(2)
        pool_ = {'name': 'pool1'}
        pool_['genesis_txn_path'] = genesis_file_path
        pool_['config'] = json.dumps({"genesis_txn": str(pool_['genesis_txn_path'])})
        await pool.create_pool_ledger_config(pool_['name'], pool_['config'])        
    except PoolLedgerConfigAlreadyExistsError:
        print('Pool', pool_['name'], ' already exsists.')
    pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)
#############################################################################    
    # 2. Create Steward Agent
    steward = {
      'name': "Sovrin Steward",
      'wallet_config': json.dumps({'id': 'sovrin_steward_wallet'}),
      'wallet_credentials': json.dumps({'key': 'steward_wallet_key'}),
      'pool': pool_['handle'],
      'seed': '000000000000000000000000Steward1'
    }
  

    try:
        await wallet.create_wallet(steward['wallet_config'], steward['wallet_credentials'])
    except WalletAlreadyExistsError:
        pass
    steward['wallet'] = await wallet.open_wallet(steward['wallet_config'], steward['wallet_credentials'])
    
    steward['did_info'] = json.dumps({'seed': steward['seed']})
    try:
        steward['did'], steward['key'] = await did.create_and_store_my_did(steward['wallet'], steward['did_info'])
    except DidAlreadyExistsError:
        pass

#############################################################################    
    # 3. Create Pseudonym(Blinded) DID for Rehuman
    # Steward Agent
    (steward['did_for_rehuman'], steward['key_for_rehuman']) = await did.create_and_store_my_did(steward['wallet'], "{}")
    # Steward Agent
    nym_request = await ledger.build_nym_request(steward['did'], steward['did_for_rehuman'], steward['key_for_rehuman'], None, 'TRUST_ANCHOR')
    await ledger.sign_and_submit_request(steward['pool'], steward['wallet'], steward['did'], nym_request)
    # Steward Agent
    connection_request = {
        'did': steward['did_for_rehuman'],
        'nonce': 123456789
    }
#############################################################################    
    # 4. Create Verinym(Public) DID for Rehuman
    # Rehuman Agent
    rehuman = {}
    await wallet.create_wallet(rehuman['wallet_config'], rehuman['wallet_credentials'])
    rehuman['wallet'] = await wallet.open_wallet(rehuman['wallet_config'], rehuman['wallet_credentials'])

    # Rehuman Agent
    (rehuman['did_for_steward'], rehuman['key_for_steward']) = await did.create_and_store_my_did(rehuman['wallet'], "{}")

    # Rehuman Agent
    connection_response = json.dumps({
        'did': rehuman['did_for_steward'],
        'verkey': rehuman['key_for_steward'],
        'nonce': connection_request['nonce']
    })

    # Rehuman Agent
    rehuman['steward_key_for_rehuman'] = await did.key_for_did(rehuman['pool'], rehuman['wallet'], connection_request['did'])

    anoncrypted_connection_response = await crypto.anon_crypt(rehuman['steward_key_for_rehuman'], connection_response.encode('utf-8'))

    # Steward Agent
    decrypted_connection_response = \
        (await crypto.anon_decrypt(steward['wallet'], steward['key_for_rehuman'], anoncrypted_connection_response)).decode("utf-8")

    # Steward Agent
    assert connection_request['nonce'] == decrypted_connection_response['nonce']

    # Steward Agent
    nym_request = await ledger.build_nym_request(steward['did'], decrypted_connection_response['did'], decrypted_connection_response['verkey'], None, role)
    print(await ledger.sign_and_submit_request(steward['pool'], steward['wallet'], steward['did'], nym_request))



#############################################################################
#############################################################################
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_rehuman())
    loop.close()

if __name__ == '__main__':
    main()


