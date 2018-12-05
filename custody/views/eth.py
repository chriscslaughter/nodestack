import datetime
from rest_framework import status
from rest_framework.response import Response
from web3 import HTTPProvider, Web3

from custody.views import BaseCoin
from custody.models import Currency
from lib.timetools import utc_now, datetime_from_utc_timestamp

class ETHCustody(BaseCoin):
    def __init__(self):
        self.cur = Currency.objects.get(symbol='ETH')
        self.w3 = Web3(Web3.HTTPProvider(self.cur.node.ip_address))

        #TODO: set addy
        self.hot_wallet_address = "0x"

    def get_status(self, request):
        final_block = self._determine_final_block()
        block = self.w3.eth.getBlock(final_block)
        cold_storage_quantity = self._to_eth(self.w3.eth.getBalance(self.cur.cold_storage_address.address))
        status_info = {
            'blocks': self._determine_final_block(),
            'required_confirmations': self.cur.required_confirmations,
            'latest_block_time': block.timestamp,
            'latest_block_age': (utc_now() - datetime.datetime.fromtimestamp(block.timestamp, datetime.timezone.utc)),
            'fee_rate': self._to_eth(self.w3.eth.gasPrice),
            'cold_storage': {
                'quantity': cold_storage_quantity,
                'value': '${:,.2f}'.format(cold_storage_quantity * self.cur.price()),
            }
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
        block = request.GET.get('block')
        if not block:
            Response({"message": "`block` must be provided"},
                     status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        starting_block = int(request.GET.get('block', 0))
        final_block = self._determine_final_block()
        block = self.w3.eth.getBlock(starting_block)
        transactions = []
        while(block and starting_block <= final_block):
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
                    transaction_details['from'].lower() == self.hot_wallet_address
                )
                if is_deposit:
                    action = 'receive'
                elif is_withdrawal:
                    action = 'send'
                else:
                    continue
                transactions.append({
                    'address': transaction_details.to,
                    'amount': transaction_details.value,
                    'confirmations': final_block - transaction_details.blockNumber,
                    'txid': transaction.hex().lower(),
                    'time_received': block.timestamp,
                    'action': action
                })
            starting_block += 1
            block = self.w3.eth.getBlock(starting_block)
        
        result = {
            "lastblock": final_block,
            "transactions": transactions
        }

        return Response(result, status=status.HTTP_200_OK)

    def submit_withdrawal(self, request, coin, format=None):
        recipient = request.data.get('address')
        amount = int(request.data.get('amount', 0))
        if not recipient or not amount:
            return Response({"msg": "Must specify address and amount."}, status=status.HTTP_400_BAD_REQUEST)

        if self.w3.eth.getBalance(self.hot_wallet_address) < amount:
            return Response({"msg": "Insufficient funds to transfer."}, status=status.HTTP_428_PRECONDITION_REQUIRED)

        transaction_details = {
            "to": self.w3.toChecksumAddress(recipient),
            "from": self.hot_wallet_address,
            "value": amount
        }
        transaction = self.w3.eth.sendTransaction(transaction_details)

        result = {
            "txid": transaction.hex(),
            "created_at": utc_now().timestamp()
        }
        return Response(result, status=status.HTTP_202_ACCEPTED)

    def _determine_final_block(self):
        final_block = self.w3.eth.blockNumber
        if not final_block:
            syncing_details = self.w3.eth.syncing
            if not syncing_details:
                raise ValueError('unable to find final block')

            """
            we use currentBlock instead of highestBlock because any block
            number higher than currentBlock won't yield any details when
            calling getBlock
            """
            if syncing_details['highestBlock']  - syncing_details['currentBlock'] \
                < self.cur.required_confirmations:
                final_block = syncing_details['highestBlock'] - self.cur.required_confirmations
        else:
            final_block = final_block - self.cur.required_confirmations

        return final_block

    def _to_eth(self, amount):
        return amount / float(1000000000000000000)
