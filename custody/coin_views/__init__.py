from abc import ABC, abstractmethod

class BaseCoin(ABC):
    @abstractmethod
    def status_get(self, request):
        pass

    @abstractmethod
    def depositsaddress_post(self):
        pass

    @abstractmethod
    def deposits_get(self):
        pass

    @abstractmethod
    def depositscoldstoragetransfer_post(self):
        pass

    @abstractmethod
    def withdrawalsaddress_post(self):
        pass

    @abstractmethod
    def withdrawals_get(self):
        pass

    @abstractmethod
    def withdrawalswithdrawal_post(self):
        pass

from custody.coin_views.btc import BTCCustody
from custody.coin_views.eth import ETHCustody
