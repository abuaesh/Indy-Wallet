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
    #cred_offer_str = input("Paste the credential offer that you recieved here: \n")
    # OR 
    cred_offer_str = '{"schema_id":"N5woRhHcnE7BBh3FwsPqFJ:2:Eduaction_Certificate:0.1","cred_def_id":"N5woRhHcnE7BBh3FwsPqFJ:3:CL:188416:edu_cert_cred_def","key_correctness_proof":{"c":"107701678349784378194732772893528409459352878141633771743765194178365350554644","xz_cap":"2362799489579001747822968685283604741964259210903789738983574830678025611991694099641148425069271469953863204030711350463429054103324986360915940113113303536089669731933000294406622601511537749925506984060033055600947594472456162898322926350008325796157740407296455958934309131379444316787267343758418736344627357575951467775525533238747269597858628044392716552733957189922961050385065592962772801811890694790723175527031002858185162620785112243378214249355921352046941046210022333208722455721814656017084068416834138067468613355645579695264057058043838817342410223059676220680636795370727719514858235344975025535043262855200418484085741569947848128530072354384925598260851493183212087216018246","xr_cap":[["first_name","958650719715452376014902015656921644227528289889896424867169527817384827206010067177477760467918303699099413999996920951836900821627138398941961170962082752688338180395055189509058607820776553733040459409196191702736545642094308135625161459718203085903094528164456991353342868086948763850100831546595549056471609618982251772657513665563947300453924141765375369582057191402163096731857159789000735618342565168360321621715303552741561251745519624001514916126855184417254022512324827594113911392763950866449036729415632020630643802286426318280187462562039325418956894260106539353508809911955689654439900193852309797207795522341288775620100810990512994027022331861023160202715892684969857459631179"],["last_name","1048579942009766158505975968336708135853362289381456526190705341013352531219091790926048878368272608387217921772930339642461866975973222650121925481601366460982759904025791150865637133990607844139713851964540822715721107210317364919547960984564659994292772988179830213890379644963577396753963093844266877915066806734814414084130844130590805756999482182430018448028847940540029667764645357455624677566029606801895330411289048774916293077477841863856851032799578434906813798859426077632427836295896608270337451121453320688756039248190039581821212913709733677358264560618143415205754659047712282833786984128823835185817219263591239792887569532725904527087990276320443435945267428352135977263842981"],["major","1740819624611899314897557776150618709507595575160780495817852807939607290228730747126602943404908585356876197360187947352693957594413983406358619158159055737635452415299897464363521657522544192428702069157176701836350715649968148666367586893064890945250467656984057410174489361835959689048246632185555658691103855442809012178655430785771058496929749456873572361169303446949343256859318507315175175416792985814485191614779579730487333925321551292182288028004292982597741425522563420216437183931074021649150361199121955332017334506902872364113069701220088488255917221580423857861450634510582843525874508787522871508015044351309396603637765421643928352005318894555349950239436234330846584204059120"],["degree","1256090089398823921100389840618785189697130152585532298308847890208931036970000415571616511799097102856334192294870785184067032868736707330842697193779499596181595199581808242325898292280194322716838603801314365177120628267170933151339812522461211045441906525344770689283363732201290924607793176596570687249886523877817808572641025102771539137565940840223497565001323175686419965963178576938223804394967274442304120945545121520051644286934594735124731838706894384719282659095376930727593757030287199529186089917569346589385068573283846283866896372420129423816728657875650056170838380779685964879033950773943216876687352799365098879888802012525363175295821489456012098230806275170180590060055167"],["master_secret","518532225121528933351258774350013817050602564854836404856915203420601089159785631271789699339621549779952838631780016403187186757941311295975644053747546075614324249868730776333469154433783406771926412593080180713109555548344448741485682259204722184298685629825219182927596426027974558373301837063451035456822566441151077265805187941334646189291508424647037208130927571031188358844056609884662122006701865123423582295733486387016901737312185463419380268983455500967800567547467197233159829211418139617806637109114149345985328134943876553531790883680406532054014961397995893580745109399551590110974401672622883622241251467800927236104763418119850573807029745788627047305305476738895916104991555"],["gpa","1162199733175062745155581951525169322031057551751831136772412009671215381877656979657755126759540928558323200020237418001169596763957708533496787376251139535096043862968883047257862332422905211686928940018537158017293387041532572252218666906903170926608931496568719498301150710537313561153977867419860547306859038966175076820950848885961412775484584020558115482339634890238183523927221793949130803701982032873261401155919854921590866584539928983425719034391081075383219913600116595002626641076736398762953705646330364413801969760393067831221796651314305688948288458866467923252757548378812604611705597706907795772603713293968137776701203441301168868722299504876443586070500090783280605226956233"],["graduation_date","1859740997993730273286240243125763208928285717701916735045614499324976497845088218065303926924368486635649065159015809591948377193426360608019605992104427694725101905354259551135319650617805835016872135062200256251651942502993255857675508032923947000171623125545421206539767210059380065118443541633360772530755115524656378934465337013391717452407946208505540895324251852013948956136171740458608856241122162215636237160934511940036430113642163801313465042377443602915168399022391633953693044533112837105045584889852017605136837672359835076555361066458261124937146535184200634362450560170497759241292903971473362900529228067916159531229909364662976756603999377413614258249179047186517226088909105"],["minor","1565163047389331957946114886106436897394692109789400725458205915767599516470562091369917708723557604125031898903115043169529582754939013237446560648908218144545984479162945706185378295574469497933607176263861309754407453241955425097374375086172956358014501731205110263382463238419146933232704030933118234278009195659037475555620098904488686456612932733254502045973144297255309246044915385968679748221080644717246776931948258720232971848814270937530320141436735086993397426925159606991819189813943584675709080451147413448679854707663938551426805831646917911956592672911180815904504777417181342707338662963219976868106742751909602985454376740422070570728718856890526500940725960516921287318582167"],["institution","225725842747438151383074109901652266315110178705124642032322822077576582092245480035996285549832501634096003614712781901986700895967197621678679540855888403362771202822921836364027235675737485327324439117352710589444340722221021310375012474167239530658634474164800600577049066326718660494912379073360304973924887299013885195237427620617102308473391410167048170238595134752500986681301931452163824142939822982597875404052935822204124491208011183624484426801118362448442696602135820530261530830879605007418155847274692205058873936552775548570763275212492535961616346839892551786257034911797825797984567791939884359782579790114583833210935845677919398843527562817984207819363450035840461390034596702255899740116277993203295350987281125493"]]},"non773007648ce":"646777300764880411051258"}'
    cred_offer_object = json.loads(cred_offer_str)

    # 2. Extract schema ID and credential definition ID from the offer
    schema_id = cred_offer_object['schema_id']
    cred_def_id = cred_offer_object['cred_def_id']

    # 3. Create and store Master Secret in Wallet
    client['master_secret_id'] = await anoncreds.prover_create_master_secret(client['wallet'], None)

    # 4. Get Credential Definition from Ledger")
    (cred_def_id, cred_def) = \
        await get_cred_def(client['pool'], client['did'], cred_def_id)

    # 5. Create Credential Request 
    (cred_request, cred_request_metadata) = \
        await anoncreds.prover_create_credential_req(client['wallet'], client['did'],
                                                    json.dumps(cred_offer_object), cred_def,
                                                     client['master_secret_id'])

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

