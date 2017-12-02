import time

from typing import List, Union
from functools import reduce

from misochain.struct import Block, Transaction, Vin, Vout
from misochain.hashing import sha256


def mine_block(block: Block, prev_block_hash: str) -> str:
    '''
    Mines a block and returns its mined hash
    '''
    hash_requirements = '0' * block.difficulty

    transactions = block.transactions

    # Get vin's and vouts in a block
    txids = reduce(lambda x, y: x + [y.txid], transactions, [])
    vins = reduce(lambda x, y: x + y.vins, transactions, [])
    vouts = reduce(lambda x, y: x + y.vouts, transactions, [])

    i = 0
    while True:
        block_hash = get_hash(
            vins=vins,
            vouts=vouts,
            txids=txids,
            prev_block_hash=prev_block_hash,
            height=block.height,
            timestamp=int(time.time()),
            difficulty=block.difficulty,
            nonce=i
        )

        if block_hash[:block.difficulty] == hash_requirements:
            return block_hash

        i = i + 1


def create_raw_tx(vins: List[Vin], vouts: List[Vout]) -> Transaction:
    '''
    Creates a new transaction object given
    a list of ins and outs
    '''
    txid = get_hash(vins=vins, vouts=vouts)
    return Transaction(txid, vins, vouts)


def sign_tx(tx: Transaction, idx: int, priv_key: str):
    '''
    Signs the transaction

    Params:
        tx: Transaction object to be signed
        idx: Index of the vin to sign
        priv_key: private key used to prove that you authorized it
    '''
    # Only use the vin for the transaction which we wanna sign
    vins = [tx.vins[idx]]
    vouts = tx.vouts
    txids = [tx.txid]
    
    tx_hash = get_hash(vins=vins, vouts=vouts, txids=txids)


def get_hash(vins: List[Vin] = [],
             vouts: List[Vout] = [],
             txids: List[str] = [],
             reward_address: str = '',
             reward_amount: Union[str, int] = '',
             prev_block_hash: str = '',
             height: Union[str, int] = '',
             timestamp: Union[str, int] = '',
             difficulty: Union[str, int] = '',
             nonce: Union[str, int] = '') -> str:
    '''
    Gets the hash given the inputs.

    Union type of str is only there so I can supply
    it an empty string by default

    Params:
        vins:           Total amount of vins
        vouts:          Total amonut of vouts
        reward_address:  Reward address of coinbase
                        (Only for Coinbase/Block type)
        reward_amount:   Reward amout of coinbase
                        (Only for Coinbase/Block type)
        prevBlockHash:  Previous block hash
        height:         Block height (only for Block type)
        difficulty:     Block difficulty (only for Block type)
        nonce:          Block nonce (only for Block type)
    '''
    # Use the of all pass vins, vouts,
    vins_str = reduce(
        lambda x, y: x + y.txid + str(getattr(y, 'index', '')),
        vins, ''
    )
    vouts_str = reduce(lambda x, y: x + y.address + str(y.value), vouts, '')
    rewards_str = reward_address + str(reward_amount)
    block_str = prev_block_hash + \
        str(height) + str(difficulty) + str(nonce) + str(timestamp)
    tx_str = reduce(lambda x, y: x + y, txids, '')

    # Order was arbitrarily chosen
    return sha256(vins_str + rewards_str + tx_str + block_str + vouts_str)