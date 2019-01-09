import datetime
import logging

from rest_framework import status
from rest_framework.response import Response
from web3 import HTTPProvider, Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy

from custody.views import BaseCoin
from custody.models import Currency
from lib.timetools import utc_now, datetime_from_utc_timestamp
from lib import to_decimal

logger = logging.getLogger(__name__)


"""
This isn't a hard limit. Before processing a new block, if the transaction
count exceeds the limit, we stop processing new blocks.
"""

class ETHCustody(BaseCoin):
    def __init__(self):
        self.cur = Currency.objects.get(symbol='ETH')
        self.w3 = Web3(Web3.HTTPProvider(self.cur.node.ip_address))
        self.w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

        #TODO: set addy
        self.hot_wallet_address = "0xd07a3060333de2002fd87e4e995227e7fab9e864"

    def get_status(self, request):
        final_block = self._determine_final_block()
        block = self.w3.eth.getBlock(final_block)
        # cold_storage_quantity = self.w3.fromWei(self.w3.eth.getBalance(self.w3.toChecksumAddress(self.cur.cold_storage_address.address)), 'ether')
        status_info = {
            'blocks': final_block,
            'latest_block_time': block.timestamp,
            'latest_block_age': (utc_now() - datetime.datetime.fromtimestamp(block.timestamp, datetime.timezone.utc)),
            'fee_rate': self.w3.fromWei(self.w3.eth.gasPrice * 21000, 'ether'),
            'required_confirmations': self.cur.required_confirmations
        }
        return Response(status_info, status=status.HTTP_200_OK)

    def get_deposit_address(self, request):
        address = self.w3.personal.newAccount("")
        address_info = {
            "address": address,
            "created_at": utc_now().timestamp()
        }
        return Response(address_info, status=status.HTTP_201_CREATED)

    def list_transactions(self, request):
        block_counter = request.GET.get('block')
        if not block_counter:
            block_counter = self.cur.default_block_height

        block_counter = int(block_counter)

        final_block = int(request.GET.get('final' ,self._determine_final_block()))
        block = self.w3.eth.getBlock(block_counter)
        transactions = []
        while(block and block_counter <= final_block):
            for transaction in block['transactions']:
                transaction_details = self.w3.eth.getTransaction(transaction)
                is_deposit = (
                    transaction_details.to and
                    transaction_details.value > 0 and
                    transaction_details.to in self.w3.eth.accounts
                )
                is_withdrawal = (
                    transaction_details.to and
                    transaction_details.value > 0 and
                    transaction_details['from'].lower() == self.hot_wallet_address.lower()
                )
                if is_deposit:
                    action = 'receive'
                elif is_withdrawal:
                    action = 'send'
                else:
                    continue
                transactions.append({
                    'address': transaction_details.to,
                    'amount': self.w3.fromWei(transaction_details.value, 'ether'),
                    'confirmations': self._determine_final_block() - transaction_details.blockNumber,
                    'txid': transaction.hex().lower(),
                    'time_received': block.timestamp,
                    'action': action
                })
            block_counter += 1
            block = self.w3.eth.getBlock(block_counter)

        result = {
            "lastblock": final_block,
            "transactions": transactions
        }

        return Response(result, status=status.HTTP_200_OK)

    def submit_withdrawal(self, request, format=None):
        recipient = request.data.get('address')
        amount = to_decimal(request.data.get('amount', 0))
        if not recipient or not amount:
            return Response({"msg": "Must specify address and amount."}, status=status.HTTP_400_BAD_REQUEST)

        if self.w3.eth.getBalance(self.w3.toChecksumAddress(self.hot_wallet_address)) < amount:
            return Response({"msg": "Insufficient funds to transfer."}, status=status.HTTP_428_PRECONDITION_REQUIRED)

        transaction_details = {
            "to": self.w3.toChecksumAddress(recipient),
            "from": self.w3.toChecksumAddress(self.hot_wallet_address),
            "value": self.w3.toWei(amount, 'ether'),
            "gas":  self.w3.generateGasPrice()
        }
        transaction = self.w3.eth.sendTransaction(transaction_details)

        result = {
            "txid": transaction.hex(),
            "created_at": utc_now().timestamp()
        }
        return Response(result, status=status.HTTP_202_ACCEPTED)

    def _determine_final_block(self):
        return self.w3.eth.blockNumber or self.w3.eth.syncing['currentBlock']
