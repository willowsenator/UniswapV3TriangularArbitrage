# https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v3


"""
    RETRIEVE GRAPH QL MID PRICES FROM UNISWAP
"""
import json
import time

import requests as requests

from src import arbitrage


def retrieve_uniswap_info():
    query = """
        query {
                pools(orderBy:totalValueLockedETH, orderDirection:desc, first:500) {
                    id
                    token0Price
                    token1Price
                    totalValueLockedETH
                    feeTier
                    token0{id symbol name decimals}
                    token1{id symbol name decimals}
                }
        }
    """
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    req = requests.post(url, json={'query': query})
    return req.json()


if __name__ == "__main__":
    while True:
        pairs = retrieve_uniswap_info()['data']['pools']
        structured_pairs = arbitrage.structure_trading_pairs(pairs, limit=500)

        # Get surface rate
        surface_rate_list = []
        for t_pair in structured_pairs:
            surface_rate = arbitrage.calc_surface_arbitrage_rate(t_pair, min_rate=1.5)
            if len(surface_rate) > 0:
                surface_rate_list.append(surface_rate)

        # Save to JSON file
        if len(surface_rate_list) > 0:
            with open("uniswapV3_surface_rate.json", "w") as fp:
                json.dump(surface_rate_list, fp)
                print("UniswapV3 JSON file saved.")

        time.sleep(60)
