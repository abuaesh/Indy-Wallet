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
from json.decoder import JSONDecodeError
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

# To store requests by this client: {cred_def_id:request_metadata}
requests = {}

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
    # await wallet.delete_wallet(wallet_config("delete", client['wallet_config']),
    #                            wallet_credentials("delete", client['wallet_credentials']))

    # print("Close and Delete pool")
    # await pool.close_pool_ledger(client['pool'])
    # await pool.delete_pool_ledger_config(pool_name)
#############################################################################    
#############################################################################
async def store_credential():
    # Ideally:
    credential = input('Paste the credential JSON:')
    credential_json = json.loads(credential)
    # credential_json = json.loads(
    #     '{"schema_id":"N5woRhHcnE7BBh3FwsPqFJ:2:Eduaction_Certificate:0.1","cred_def_id":"N5woRhHcnE7BBh3FwsPqFJ:3:CL:188416:cd11","rev_reg_id":null,"values":{"minor":{"raw":"k","encoded":"8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a"},"graduation_date":{"raw":"k","encoded":"8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a"},"first_name":{"raw":"k","encoded":"8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a"},"major":{"raw":"k","encoded":"8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a"},"gpa":{"raw":"k","encoded":"8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a"},"institution":{"raw":"k","encoded":"8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a"},"degree":{"raw":"k","encoded":"8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a"},"last_name":{"raw":"k","encoded":"8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a"}},"signature":{"p_credential":{"m_2":"82381463374636253200201623950741530277113131912631715290315983012197005369555","a":"17995055234646938952189889487242525502440298831635681830473071130597438040944460923290247241706219865528493425392134520746264427609728809970016603682221887613859341266833834239266353154142535016018976285864390469151677820495845596508477173546903234154783943978888026118456140418850046311967544130255370690481267019612988978193354987901947504586528561570161203636802581019365979102531501856266169746479438569540197331907557098466158815300952113369749774472073735653500878924351118749886597115908249382180133749958066975022983709300650041766700952426467660735854812019860226574265594207523278153165797606244627438145571","e":"259344723055062059907025491480697571938277889515152306249728583105665800713306759149981690559193987143012367913206299323899696942213235956742930027630075093033538055643618396818089","v":"5677585060886190698910015480983799469771171931205478324467905791664363547593193729027761203649423015842856868783927933744056131587338532030833610372162002786320851114885723129558292164190026515787610859499696081575961363871053338239378507887379181316911600394883674189787820858963936013994228950546510601824702089829325987178452551679895861961829359804225540247878099831126339818347554411574320189749479972065534553298269721626737254514946612478102511937412268247258500227114274383500622225613821843763118888029913151269192638324674930919215326366573895357589412912210241696853977949099974689646633392969961997393715728149193563891406797226587241974739080418013849202681216413263842762553756231108147925455697534934913522640797053166160623670868051389606161122575763648237958751295851622638903013967697644393758066120634"},"r_credential":null},"signature_correctness_proof":{"se":"18940660870051775277922471172979745478833011510383191582376045491918046778065498956965327711862989448525680337817546338586037434630176677653467573380619311820055632580034757962609301773907768169704826148169024440082432381403429290244581278381319940312738029452113565097444510913604110209574232185191385437513289275113814808425163532610520042653996279434583667858100958256814513310827073790538883149307274511451060387795112833319186518182366784284464430940777628347585367444316752823337910169753947690824875265186802380658410963915374168598622379260450422803571891561575464492484515452726456907306802860570513516587843","c":"10298918761506918809776162245750587819665581666201125096404079403372384543124"},"rev_reg":null,"witness":null}'
    # )
    
    try:
        revocation_enabled = credential_json['rev_reg_id']
    except NameError: # NameError: name 'null' is not defined
        revocation_enabled = None


    if revocation_enabled == None:
        revoc_reg_def_json = None
    else:
        revoc_reg_def_json = await get_rev_reg_def(client['pool'], client['did'], credential_json['rev_reg_id'])

    credential_definition = await get_cred_def(client['pool'], client['did'], credential_json['cred_def_id'])

    try:
        print(await anoncreds.prover_store_credential(client['wallet'], None, 
                                            json.dumps(requests[credential_json['cred_def_id']]),
                                            json.dumps(credential_json), json.dumps(credential_definition), 
                                            json.dumps(revoc_reg_def_json)))
    except CommonInvalidStructure:
            print('Credential successfully saved to your wallet')
#############################################################################
#############################################################################
async def get_rev_reg_def(pool_handle, _did, rev_reg_id):
    revoc_reg_des_req = \
        await ledger.build_get_revoc_reg_def_request(_did, rev_reg_id)
    revoc_reg_des_resp = await ledger.submit_request(pool_handle, revoc_reg_des_req)
    (revoc_reg_def_id, revoc_reg_def_json) = \
        await ledger.parse_get_revoc_reg_def_response(revoc_reg_des_resp)
    return revoc_reg_def_json
#############################################################################
#############################################################################
async def accept_credential_offer():

    # 1. Get credential offer
    invalid_offer = True
    while invalid_offer:
        try:
            cred_offer_str = input("Paste the credential offer that you recieved here: \n")
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

    # 6. Store request metadata for future access-needed when storing credential to the wallet
    requests[json.loads(cred_request)['cred_def_id']] = cred_request_metadata
    # 7. Send Credential Request to Issuer
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

