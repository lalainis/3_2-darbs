class PriceStrategy:
    def prepare_data(self, prices):
        pass
class BitcoinPriceStrategy(PriceStrategy):
    def prepare_data(self, prices):
        return [price["bitcoin"] for price in prices]
class EthereumPriceStrategy(PriceStrategy):
    def prepare_data(self, prices):
        return [price["ethereum"] for price in prices]
class StrategyFactory:
    def create(self, asset_type):
        if asset_type == "bitcoin":
            return BitcoinPriceStrategy()
        elif asset_type == "ethereum":
            return EthereumPriceStrategy()
prices = [
    {"bitcoin": 65000, "ethereum": 3200},
    {"bitcoin": 66000, "ethereum": 3300},
    {"bitcoin": 65500, "ethereum": 3250}
]
strategy = StrategyFactory().create("dogecoin")
print(strategy.prepare_data(prices))