forward = "forward"
reverse = "reverse"
base_to_quote = "baseToQuote"
quote_to_base = "quoteToBase"


# Structure trading pair groups
def structure_trading_pairs(pairs, limit):
    triangular_pairs_list = []
    remove_duplicates_list = []
    pairs_list = pairs[:limit]

    # Get first pair (A)
    for pair_a in pairs_list:
        a_base = pair_a["token0"]["symbol"]
        a_quote = pair_a["token1"]["symbol"]
        a_pair = a_base + "_" + a_quote
        a_contract = pair_a["id"]
        a_token0_id = pair_a["token0"]["id"]
        a_token1_id = pair_a["token1"]["id"]
        a_token0_decimals = pair_a["token0"]["decimals"]
        a_token1_decimals = pair_a["token1"]["decimals"]
        a_token0_price = pair_a["token0Price"]
        a_token1_price = pair_a["token1Price"]

        # Put (A) into box for checking at (B)
        a_pair_box = [a_base, a_quote]

        # Get second pair (B)
        for pair_b in pairs_list:
            b_base = pair_b["token0"]["symbol"]
            b_quote = pair_b["token1"]["symbol"]
            b_pair = b_base + "_" + b_quote
            b_contract = pair_b["id"]
            b_token0_id = pair_b["token0"]["id"]
            b_token1_id = pair_b["token1"]["id"]
            b_token0_decimals = pair_b["token0"]["decimals"]
            b_token1_decimals = pair_b["token1"]["decimals"]
            b_token0_price = pair_b["token0Price"]
            b_token1_price = pair_b["token1Price"]

            # Get third pair (C)
            if a_pair != b_pair:
                if b_base in a_pair_box or b_quote in a_pair_box:
                    for pair_c in pairs_list:
                        c_base = pair_c["token0"]["symbol"]
                        c_quote = pair_c["token1"]["symbol"]
                        c_pair = c_base + "_" + c_quote
                        c_contract = pair_c["id"]
                        c_token0_id = pair_c["token0"]["id"]
                        c_token1_id = pair_c["token1"]["id"]
                        c_token0_decimals = pair_c["token0"]["decimals"]
                        c_token1_decimals = pair_c["token1"]["decimals"]
                        c_token0_price = pair_c["token0Price"]
                        c_token1_price = pair_c["token1Price"]

                        # Count number of (C) items
                        if a_pair != c_pair and b_pair != c_pair:
                            combine_all = [a_pair, b_pair, c_pair]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                            count_c_base = 0
                            count_c_quote = 0
                            for i in pair_box:
                                if i == c_base:
                                    count_c_base += 1
                                elif i == c_quote:
                                    count_c_quote += 1

                            if count_c_base == 2 and count_c_quote == 2 and c_base != c_quote:
                                combined = a_pair + "|" + b_pair + "|" + c_pair
                                unique_string = ''.join(sorted(combine_all))

                                # Output pair
                                if unique_string not in remove_duplicates_list:
                                    output_dict = {
                                        "aPair": a_pair,
                                        "aBase": a_base,
                                        "aQuote": a_quote,
                                        "bPair": b_pair,
                                        "bBase": b_base,
                                        "bQuote": b_quote,
                                        "cPair": c_pair,
                                        "cBase": c_base,
                                        "cQuote": c_quote,
                                        "combined": combined,
                                        "aContract": a_contract,
                                        "bContract": b_contract,
                                        "cContract": c_contract,
                                        "aToken0Id": a_token0_id,
                                        "aToken1Id": a_token1_id,
                                        "bToken0Id": b_token0_id,
                                        "bToken1Id": b_token1_id,
                                        "cToken0Id": c_token0_id,
                                        "cToken1Id": c_token1_id,
                                        "aToken0Decimals": a_token0_decimals,
                                        "aToken1Decimals": a_token1_decimals,
                                        "bToken0Decimals": b_token0_decimals,
                                        "bToken1Decimals": b_token1_decimals,
                                        "cToken0Decimals": c_token0_decimals,
                                        "cToken1Decimals": c_token1_decimals,
                                        "aToken0Price": a_token0_price,
                                        "aToken1Price": a_token1_price,
                                        "bToken0Price": b_token0_price,
                                        "bToken1Price": b_token1_price,
                                        "cToken0Price": c_token0_price,
                                        "cToken1Price": c_token1_price,
                                    }
                                    triangular_pairs_list.append(output_dict)
                                    remove_duplicates_list.append(unique_string)
    return triangular_pairs_list


# Calculate Surface Arbitrage Potencial
def calc_surface_arbitrage_rate(t_pair, min_rate):
    surface_dict = {}
    min_surface_rate = min_rate
    pool_contract_2 = ""
    pool_contract_3 = ""
    pool_direction_trade_1 = ""
    pool_direction_trade_2 = ""
    pool_direction_trade_3 = ""

    # Set directions
    direction_list = [forward, reverse]
    for direction in direction_list:

        # Set pair info
        a_base = t_pair["aBase"]
        a_quote = t_pair["aQuote"]
        b_base = t_pair["bBase"]
        b_quote = t_pair["bQuote"]
        c_base = t_pair["cBase"]
        c_quote = t_pair["cQuote"]

        # Set price Info
        a_token0_price = float(t_pair["aToken0Price"])
        a_token1_price = float(t_pair["aToken1Price"])
        b_token0_price = float(t_pair["bToken0Price"])
        b_token1_price = float(t_pair["bToken1Price"])
        c_token0_price = float(t_pair["cToken0Price"])
        c_token1_price = float(t_pair["cToken1Price"])

        # Set addressInfo
        a_contract = t_pair["aContract"]
        b_contract = t_pair["bContract"]
        c_contract = t_pair["cContract"]

        # Set Variables
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0

        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0

        starting_amount = 1
        acquired_coin_t2 = 0
        acquired_coin_t3 = 0
        calculated = 0

        """
           Uniswap V3 rule!!
            If we are swapping from left (base) to right (quote) * token1_price
            If we are swapping from right (quote) to left (base) * token0_price
        """

        # Assuming starting with a_base swapping a_quote
        if direction == forward:
            swap_1 = a_base
            swap_2 = a_quote
            swap_1_rate = a_token1_price
            pool_direction_trade_1 = base_to_quote

        # Assuming starting with a_quote swapping a_base
        if direction == reverse:
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_token0_price
            pool_direction_trade_1 = quote_to_base

        # Place first trade
        pool_contract_1 = a_contract
        acquired_coin_t1 = starting_amount * swap_1_rate

        """ FORWARD """
        # SCENARIO 1 Check if a_quote (acquired_coin) matches b_quote
        if direction == forward:
            if a_quote == b_quote and calculated == 0:
                swap_2_rate = b_token0_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                pool_direction_trade_2 = quote_to_base
                pool_contract_2 = b_contract

                # If b_base (acquired_coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = c_token1_price
                    pool_direction_trade_3 = base_to_quote
                    pool_contract_3 = c_contract

                # If b_base (acquired_coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_token0_price
                    pool_direction_trade_3 = quote_to_base
                    pool_contract_3 = c_contract

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 2 Check if a_quote (acquired_coin) matches b_base
        if direction == forward:
            if a_quote == b_base and calculated == 0:
                swap_2_rate = b_token1_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                pool_direction_trade_2 = base_to_quote
                pool_contract_2 = b_contract

                # If b_quote (acquired_coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = c_token1_price
                    pool_direction_trade_3 = base_to_quote
                    pool_contract_3 = c_contract

                # If b_quote (acquired_coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_token0_price
                    pool_direction_trade_3 = quote_to_base
                    pool_contract_3 = c_contract

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 3 Check if a_quote (acquired_coin) matches c_quote
        if direction == forward:
            if a_quote == c_quote and calculated == 0:
                swap_2_rate = c_token0_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                pool_direction_trade_2 = quote_to_base
                pool_contract_2 = c_contract

                # If c_base (acquired_coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = b_token1_price
                    pool_direction_trade_3 = base_to_quote
                    pool_contract_3 = b_contract

                # If c_base (acquired_coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_token0_price
                    pool_direction_trade_3 = quote_to_base
                    pool_contract_3 = b_contract

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 4 Check if a_quote (acquired_coin) matches c_base
        if direction == forward:
            if a_quote == c_base and calculated == 0:
                swap_2_rate = c_token1_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                pool_direction_trade_2 = base_to_quote
                pool_contract_2 = c_contract

                # If c_quote (acquired_coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = b_token1_price
                    pool_direction_trade_3 = base_to_quote
                    pool_contract_3 = b_contract

                # If c_quote (acquired_coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_token0_price
                    pool_direction_trade_3 = quote_to_base
                    pool_contract_3 = b_contract

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        """ REVERSE """
        # SCENARIO 1 Check if a_base (acquired_coin) matches b_quote
        if direction == reverse:
            if a_base == b_quote and calculated == 0:
                swap_2_rate = b_token0_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                pool_direction_trade_2 = quote_to_base
                pool_contract_2 = b_contract

                # If b_base (acquired_coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = c_token1_price
                    pool_direction_trade_3 = base_to_quote
                    pool_contract_3 = c_contract

                # If b_base (acquired_coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_token0_price
                    pool_direction_trade_3 = quote_to_base
                    pool_contract_3 = c_contract

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 2 Check if a_base (acquired_coin) matches b_base
        if direction == reverse:
            if a_base == b_base and calculated == 0:
                swap_2_rate = b_token1_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                pool_direction_trade_2 = base_to_quote
                pool_contract_2 = b_contract

                # If b_quote (acquired_coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = c_token1_price
                    pool_direction_trade_3 = base_to_quote
                    pool_contract_3 = c_contract

                # If b_quote (acquired_coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_token0_price
                    pool_direction_trade_3 = quote_to_base
                    pool_contract_3 = c_contract

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 3 Check if a_base (acquired_coin) matches c_quote
        if direction == reverse:
            if a_base == c_quote and calculated == 0:
                swap_2_rate = c_token0_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                pool_direction_trade_2 = quote_to_base
                pool_contract_2 = c_contract

                # If c_base (acquired_coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = b_token1_price
                    pool_direction_trade_3 = base_to_quote
                    pool_contract_3 = b_contract

                # If c_base (acquired_coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_token0_price
                    pool_direction_trade_3 = quote_to_base
                    pool_contract_3 = b_contract

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 4 Check if a_base (acquired_coin) matches c_base
        if direction == reverse:
            if a_base == c_base and calculated == 0:
                swap_2_rate = c_token1_price
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                pool_direction_trade_2 = base_to_quote
                pool_contract_2 = c_contract

                # If c_quote (acquired_coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = b_token1_price
                    pool_direction_trade_3 = base_to_quote
                    pool_contract_3 = b_contract

                # If c_quote (acquired_coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_token0_price
                    pool_direction_trade_3 = quote_to_base
                    pool_contract_3 = b_contract

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        """ PROFIT LOSS """
        # Profit and Loss calculations
        profit_loss = acquired_coin_t3 - starting_amount
        profit_loss_percentage = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

        # Output results
        if profit_loss_percentage >= min_surface_rate:
            # Trade Descriptions
            trade_description_1 = f"Starting with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2}" \
                                  f" acquiring {acquired_coin_t1}. "
            trade_description_2 = f"Swap {acquired_coin_t1} of {swap_2} at {swap_2_rate} for {swap_3} acquiring " \
                                  f"{acquired_coin_t2}. "
            trade_description_3 = f"Swap {acquired_coin_t2} of {swap_3} at {swap_3_rate} for {swap_1} acquiring " \
                                  f"{acquired_coin_t3}. "

            surface_dict = {
                "swap1": swap_1,
                "swap2": swap_2,
                "swap3": swap_3,
                "poolContract1": pool_contract_1,
                "poolContract2": pool_contract_2,
                "poolContract3": pool_contract_3,
                "poolDirectionTrade1": pool_direction_trade_1,
                "poolDirectionTrade2": pool_direction_trade_2,
                "poolDirectionTrade3": pool_direction_trade_3,
                "startingAmount": starting_amount,
                "acquiredCoinT1": acquired_coin_t1,
                "acquiredCoinT2": acquired_coin_t2,
                "acquiredCoinT3": acquired_coin_t3,
                "swap1Rate": swap_1_rate,
                "swap2Rate": swap_2_rate,
                "swap3Rate": swap_3_rate,
                "profitLoss": profit_loss,
                "profitLossPercentage": profit_loss_percentage,
                "direction": direction,
                "tradeDescription1": trade_description_1,
                "tradeDescription2": trade_description_2,
                "tradeDescription3": trade_description_3,
            }
            return surface_dict
    return surface_dict
