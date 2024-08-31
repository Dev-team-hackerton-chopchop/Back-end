# vote/xrpl_utils.py

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

def create_wallet():
    wallet = generate_faucet_wallet(client, debug=True)
    return wallet


def cast_vote(wallet, post_id, option, vote_choice):
    # 매번 새로운 무작위 지갑을 생성
    sender_wallet = create_wallet()
    
    receiver_address = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"  # 고정된 Receiver 주소
    
    memo_data = f"Post ID:{post_id},Choice:{vote_choice}"
    
    vote_tx = Payment(
        account=sender_wallet.classic_address,  # 무작위로 생성된 sender_wallet 사용
        amount="1",
        destination=receiver_address,  # 고정된 Receiver 주소로 트랜잭션 발생
        memos=[Memo(
            memo_data=memo_data.encode("utf-8").hex(),
            memo_format="text/plain".encode("utf-8").hex(),
            memo_type="vote/cast".encode("utf-8").hex()
        )]
    )
    
    # 트랜잭션에 자동으로 필요한 필드를 채우고 서명
    signed_tx = autofill_and_sign(vote_tx, client, sender_wallet)
    response = submit_and_wait(signed_tx, client)
    
    if response.is_successful():
        print(f"Transaction completed by wallet {sender_wallet.classic_address}. Memo data: {memo_data}")
        return {
            "hash": response.result['hash'],
            "memo": memo_data
        }
    else:
        raise ValueError("Transaction failed or unexpected response structure")


def tally_votes(wallet, post_id):
    account_tx_request = AccountTx(account=wallet.classic_address, binary=False)
    response = client.request(account_tx_request)

    o_count = 0
    x_count = 0
    
    for tx in response.result['transactions']:
        tx_data = tx.get('tx_json', {})
        
        if 'Memos' in tx_data:
            for memo in tx_data['Memos']:
                memo_data_hex = memo['Memo'].get('MemoData', None)
                
                if memo_data_hex:
                    memo_data = bytes.fromhex(memo_data_hex).decode('utf-8')
                    
                    parts = memo_data.split(',')
                    post_id_part = parts[0].split(':')[1]
                    choice_part = parts[1].split(':')[1]
                    
                    if post_id_part == post_id:
                        if choice_part == "O":
                            o_count += 1
                        elif choice_part == "X":
                            x_count += 1
    
    return {"O": o_count, "X": x_count}
