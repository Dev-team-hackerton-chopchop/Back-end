import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment, Memo
from xrpl.models.requests import AccountTx, AccountInfo
from xrpl.wallet import generate_faucet_wallet
from xrpl.transaction import autofill_and_sign, submit_and_wait
import nest_asyncio
import time

# asyncio 관련 에러 해결을 위한 nest_asyncio 적용
nest_asyncio.apply()

# XRP Ledger 클라이언트 설정
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"  # 테스트넷 URL
client = JsonRpcClient(JSON_RPC_URL)

def create_wallet():
    # Wallet 생성
    wallet = generate_faucet_wallet(client, debug=True)
    return wallet

def check_balance(wallet):
    # 잔액 확인
    account_info = client.request(AccountInfo(account=wallet.classic_address))
    balance = account_info.result['account_data']['Balance']
    print(f"Account balance: {balance}")
    return balance

def create_vote(wallet, vote_id, vote_topic, options):
    # 더미 주소 사용
    dummy_address = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"
    
    # 투표를 생성하는 함수
    memo_data = f"VOTE:{vote_id}:{vote_topic}:{','.join(options)}"
    create_vote_tx = Payment(
        account=wallet.classic_address,
        amount="1",
        destination=dummy_address,
        memos=[Memo(
            memo_data=memo_data.encode("utf-8").hex(),
            memo_format="text/plain".encode("utf-8").hex(),
            memo_type="vote/create".encode("utf-8").hex()
        )]
    )
    
    # 트랜잭션 자동 완성 및 서명
    signed_tx = autofill_and_sign(create_vote_tx, client, wallet)
    
    # 트랜잭션 제출 및 결과 확인
    response = submit_and_wait(signed_tx, client)
    
    if response.is_successful():
        print("Vote creation transaction was successfully submitted!")
        print("Transaction hash:", response.result['hash'])
        return response.result['hash']
    else:
        print("Vote creation failed:", response.result)
        raise ValueError("Transaction failed or unexpected response structure")

def cast_vote(wallet, vote_id, option, vote_choice):
    # 더미 주소 사용
    dummy_address = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"
    
    # Memo 데이터에 투표 ID, 옵션, 그리고 선택한 투표 결과 (O/X) 포함
    memo_data = f"VOTE:{vote_id}:{option}:{vote_choice}"
    
    vote_tx = Payment(
        account=wallet.classic_address,
        amount="1",
        destination=dummy_address,
        memos=[Memo(
            memo_data=memo_data.encode("utf-8").hex(),
            memo_format="text/plain".encode("utf-8").hex(),
            memo_type="vote/cast".encode("utf-8").hex()
        )]
    )
    signed_tx = autofill_and_sign(vote_tx, client, wallet)
    response = submit_and_wait(signed_tx, client)
    
    if response.is_successful():
        print("Vote cast transaction was successfully submitted!")
        print("Transaction hash:", response.result['hash'])
        return response.result['hash']
    else:
        print("Vote casting failed:", response.result)
        raise ValueError("Transaction failed or unexpected response structure")
    
def tally_votes(wallet, vote_id):
    # 트랜잭션 조회시 binary=False 설정
    account_tx_request = AccountTx(account=wallet.classic_address, binary=False)
    response = client.request(account_tx_request)

    print("Account Transactions Response:", response.result)
    
    memo_summaries = []
    # 트랜잭션을 순회하며 Memo 데이터를 찾음
    for i, tx in enumerate(response.result['transactions']):
        # tx_json 필드에서 실제 트랜잭션 데이터를 가져옴
        tx_data = tx.get('tx_json', {})
        
        print(f"Transaction {i+1} - Hash: {tx_data.get('hash')}")
        
        if 'Memos' in tx_data:
            print(f"Memos found in Transaction {i+1}")
            for memo in tx_data['Memos']:
                memo_data_hex = memo['Memo'].get('MemoData', None)
                
                if memo_data_hex:
                    # 헥사코드를 UTF-8 문자열로 디코딩
                    memo_data = bytes.fromhex(memo_data_hex).decode('utf-8')
                    print(f"Decoded MemoData from Transaction {i+1}: {memo_data}")
                    
                    # MemoData를 분석하여 요약 정보 추출
                    parts = memo_data.split(':')
                    if len(parts) >= 4:
                        vote_id = parts[1]
                        option = parts[2]
                        vote_choice = parts[3]
                        summary = {
                            'Transaction': i + 1,
                            'Vote ID': vote_id,
                            'Option': option,
                            'Vote': vote_choice
                        }
                        memo_summaries.append(summary)
                    else:
                        print(f"Unexpected Memo format in Transaction {i+1}: {memo_data}")
                else:
                    print(f"MemoData not found in Memos of Transaction {i+1}")
        else:
            print(f"No Memos found in Transaction {i+1}")
    
    if not memo_summaries:
        print("No memo summaries were collected across all transactions.")
    else:
        print("\nMemo Summaries from all transactions:")
        for summary in memo_summaries:
            print(f"Transaction {summary['Transaction']}: Vote ID {summary['Vote ID']}, Option: {summary['Option']}, Vote: {summary['Vote']}")
    
    return memo_summaries

def main():
    wallet = create_wallet()
    
    # 잔액 확인
    check_balance(wallet)

    vote_id = "001"
    vote_topic = "Favorite Programming Language"
    options = ["Python", "JavaScript", "Rust", "Go"]
    first_vote_hash = create_vote(wallet, vote_id, vote_topic, options)

    # 각 트랜잭션마다 대기 시간을 추가
    time.sleep(5)
    cast_vote(wallet, vote_id, "Python", "O")
    time.sleep(5)
    cast_vote(wallet, vote_id, "JavaScript", "X")
    time.sleep(5)
    cast_vote(wallet, vote_id, "Rust", "O")
    time.sleep(5)
    cast_vote(wallet, vote_id, "Go", "X")

    results = tally_votes(wallet, vote_id)
    print("Final Memo Summaries:", results)

main()


