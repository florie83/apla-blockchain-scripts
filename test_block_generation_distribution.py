
from genesis_blockchain_api_client.session import Session
import time

s = Session("http://127.0.0.1:7049/api/v2")


while True:
    max_block_id = s.get_max_block_id()

    cnt = dict()
    for i in range(1, max_block_id):
        bl = s.get_detailed_block_data(i)
        # print(bl)
        key_id = bl['key_id']
        cnt[key_id] = cnt.get(key_id, 0) + 1

    print(cnt)
    time.sleep(3)