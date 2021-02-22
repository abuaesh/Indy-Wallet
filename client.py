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
    cred_offer_object = {"schema_id":"N5woRhHcnE7BBh3FwsPqFJ:2:Record_Of_Employment:0.1","cred_def_id":"N5woRhHcnE7BBh3FwsPqFJ:3:CL:188417:testdef","key_correctness_proof":{"c":"23870929130462062602121056086719571550894254638575268504478662327119120687386","xz_cap":"435221938167350126325097893000838110135132903513625128305292386536060533507032068755913990223752999734072626204869460866273316284645254147563704905484573335988635948511560230898549954557928575399336408837034200318818855997499008997035352349737983481205445860837020855748195403076896170427462997483992169325823152914814814454147097327943024915373987413974818237764436180897848733964298798756888796641404902359855699369014256676861081839489281441907185927830891971957828265622735412165256553993063950674220869052536188814609788858884063420978673568162104639536974403038790387747696371685975022221857631632121095815307217788837467300890520225074812864491165011851721332480044186189698642022912547","xr_cap":[["leaving_year","195188048464630248928136859177674442143041402326036180629114603345010338925206018704057371240763585707859127426012822109117188964089610326123642164285213151887004924955523931494208418916085925150097511125674484181860149769304144870983363950016999041550603907115547413134485132264075792374317666923583365040475679620749046009080720305236759970047584374353797549663545797854764884493107065767909554819085477247426479140538164274433626113670764799858719866184976130834421641273993789121310049654214020892356650322441008336195845506178246954596263834425421320109633092307869421873216145112391753724431755568466419898802432087953268535814156524546906808821453125607564819568886620800340036055564559"],["joining_year","570105571268360631891370266686596416288295504963906347089337268326439354665009639803372839884383810414667048976158457849761383682053819191587554273026154743534350810228096996575779483787014986154572339768201799316680195097917484461137145787881357612526402538032000375952394046616918705265364746300083168074066496401551380775339751036274013466659145320525889442451602942153779772681460707614733403812627643051795308446676955251115515396559472846360467348022211659562502265835374521051805092403845265633873166782282304745510171645443682893829442302960718704059138721538700370671904883235162213412227321847286448781441508773435655900776524484659607067278903096025285569716846325072803043583958050"],["job_title","20986738855849173989355856201718391385244447239163146789882771247846437876732481198793649124278292485931027068026546594282673369479571977323352257383270810647699295312812773362185975299433031157500237356418006394745132609163488560453519114536081590682076189199574424718232526433351722082968398759413306891577880983491867654175747216158899405552711075600034472768051045610351621877051844037744025901049289063130949624953685791786238268327339494804832427299778054629324055827220157515654325206760272566019002472179550979304236547894792015076409723734954920236032261595620614794741978368931645490371730733786298687215871618464533861661873447995984168707327067411911431087461923254325971343823951"],["master_secret","297834157418475957889257854490633534719696909598857631598557164683722429706254918172401514205774216609689346085572479202816730872352630285112900491642005031582896355446782499001997019070658746309844847147635863689866562577617974774715791371602178856732833144497752226385586490903543297704009053580610574620431639648130702611707752773329269138737609398599152369419868555816593221202515072655254021314816800350733319662669565968276479837428254518278323115691892265302349190302636471792357253663703391308427427481225569210320830561965614042127614020359835706900136747224218754406920326385595552082121610653520464545603921582922358234966993166701172441280989655479903924465823027925734946332729466"],["first_name","37279037708657360249291903644919525015276473163607378647427343643923380944433601653103956122959354049742606275322550696121245995283924945564284046362921195212858217388947350349690903987057570765164410905603285019995066724449773042322311907056036020386133031460018412245406985391881479444541746083131099051668032787322919040988399044936154006908293021881754868179060321847137588605188551503596832923443562829550632428886403610855043753842165542960869082631047731594519687540556050553917339579358072804526067464174232273639681632361942449918852580033837504335076372020579699500295146377849892987343477210567957791455043962881808386089021249375060472808454130363300649725759614598243021768742101"],["last_name","195193054390688462121492922080376894650516719741075420640260301528905515509513189092264996487400868797333171918683047706121507338325204408138611686338036765628678927364493730577926422831866300971637762287135563786749997886927860428454409673723389779882805397686108807995649682242808367806241289968476644395840036926132214046646835953850118825642486053503532014353114285748274382332497345859879363988675716540505431371794428621255004326042096548551414325609815770297932273536370219943392707534313361707690679398757639317677882952959627390990778989431131797849642663223979957067401875626385253747999652189700499878392221936093579058674756777640528675086133965433002461565742862809858181630000440"],["employer","119217495584340038936639384393323764245411489577006150236430023333942196881357895385132424870801046697194907952391942738539658772276571476782652534312960023228836296984509815432340525695614027568845578106952463454584703047225295299214879611919816737759529210931210481410529520718377072544735410446000325025679906928572160425327880248267178326307205853514516772933013876149230906298852066774213349663608556399676241522599977555698221651865001958809980323625607025115579898051037558593464738193356656324295036105215898527609742747844252925488465757192398482279262624914250860768466582703004304403452183704955569125779909127632913115465795149816502930221319144181738968654405851184827144075798254"],["reason_of_leaving","199872138107309419273886301487428329393141329512281284333868314389636725926341732359644318393306448451585027806087406959614926154981113714227996457188796318981820585692927196902782826591645523199640092710341596750783648208544282391585767263835024039829657524271648368807820642313546851283867448560342615653271618836007176623103620353866225200758248471348956690902189360666899256374985148574451304909119912249891868221037242493356301685909877192350139683715563189492557110663968532234911531906075508424273411998811589625609613255966155367117102074015204740344413340625885968261404077532903946774425845741673253063122162204548582455428824908696740067677305604768375631433802758483517699398721971"]]},"nonce":"1201783823135024289190909"}
    cred_offer_str = json.dumps(cred_offer_object)

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

