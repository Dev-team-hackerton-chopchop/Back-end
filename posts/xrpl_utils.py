import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment, Memo
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.requests import AccountTx
from xrpl.transaction import autofill_and_sign, submit_and_wait
import nest_asyncio

# asyncio 관련 에러 해결을 위한 nest_asyncio 적용
nest_asyncio.apply()

# XRP Ledger 클라이언트 설정
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"  # 테스트넷 URL
client = JsonRpcClient(JSON_RPC_URL)

# 하나의 지갑 주소만 사용하기 위해 전역적으로 지갑 생성
wallet = generate_faucet_wallet(client, debug=True)

def get_wallet():
    return wallet

def cast_vote(wallet, post_id, option, vote_choice):
    receiver_address = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"  # 고정된 Receiver 주소
    
    memo_data = f"Post ID:{post_id},Choice:{vote_choice}"
    
    vote_tx = Payment(
        account=wallet.classic_address,  # 동일한 wallet 사용
        amount="1",
        destination=receiver_address,  # 고정된 Receiver 주소로 트랜잭션 발생
        memos=[Memo(
            memo_data=memo_data.encode("utf-8").hex(),
            memo_format="text/plain".encode("utf-8").hex(),
            memo_type="vote/cast".encode("utf-8").hex()
        )]
    )
    
    # 트랜잭션에 자동으로 필요한 필드를 채우고 서명
    signed_tx = autofill_and_sign(vote_tx, client, wallet)
    response = submit_and_wait(signed_tx, client)
    
    if response.is_successful():
        print(f"Transaction completed by wallet {wallet.classic_address}. Memo data: {memo_data}")
        return {
            "hash": response.result['hash'],
            "memo": memo_data
        }
    else:
        raise ValueError("Transaction failed or unexpected response structure")

def tally_votes(wallet, vote_id):
    # 트랜잭션 조회시 binary=False 설정
    account_tx_request = AccountTx(account=wallet.classic_address, binary=False)
    response = client.request(account_tx_request)

    print("Account Transactions Response:", response.result)
    
    memo_summaries = {"O": 0, "X": 0}  # O와 X 투표 수를 기록할 딕셔너리
    
    # 트랜잭션을 순회하며 Memo 데이터를 찾음
    for i, tx in enumerate(response.result['transactions']):
        # tx_json 필드에서 실제 트랜잭션 데이터를 가져옴
        tx_data = tx.get('tx', {}) or tx.get('tx_json', {})
        
        print(f"Transaction {i+1} - Hash: {tx_data.get('hash', 'N/A')}")
        
        if 'Memos' in tx_data:
            print(f"Memos found in Transaction {i+1}")
            for memo in tx_data['Memos']:
                memo_data_hex = memo['Memo'].get('MemoData', None)
                
                if memo_data_hex:
                    # 헥사코드를 UTF-8 문자열로 디코딩
                    memo_data = bytes.fromhex(memo_data_hex).decode('utf-8')
                    print(f"Decoded MemoData from Transaction {i+1}: {memo_data}")
                    
                    # MemoData를 분석하여 요약 정보 추출
                    parts = memo_data.split(',')
                    if len(parts) == 2:
                        post_id_part = parts[0].split(':')[1].strip()
                        vote_choice_part = parts[1].split(':')[1].strip()
                        
                        if post_id_part == vote_id:
                            if vote_choice_part in memo_summaries:
                                memo_summaries[vote_choice_part] += 1
                            else:
                                print(f"Unexpected vote choice in Transaction {i+1}: {vote_choice_part}")
                    else:
                        print(f"Unexpected Memo format in Transaction {i+1}: {memo_data}")
                else:
                    print(f"MemoData not found in Memos of Transaction {i+1}")
        else:
            print(f"No Memos found in Transaction {i+1}")
    
    print(f"\nFinal Tally: O = {memo_summaries['O']}, X = {memo_summaries['X']}")
    
    return memo_summaries
