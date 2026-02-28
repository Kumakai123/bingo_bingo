"""
BINGO BINGO 賓果賓果完整賠率表

所有倍數基於每注 NT$25 計算。
資料來源：台灣彩券官方規則
"""

# key = (star_level, matched_count), value = 獎金倍數
BASIC_PAYOUT: dict[tuple[int, int], int] = {
    # 1 星
    (1, 1): 2,
    # 2 星
    (2, 2): 3,
    (2, 1): 1,
    # 3 星
    (3, 3): 20,
    (3, 2): 2,
    # 4 星
    (4, 4): 40,
    (4, 3): 4,
    (4, 2): 1,
    # 5 星
    (5, 5): 300,
    (5, 4): 20,
    (5, 3): 2,
    # 6 星
    (6, 6): 1_000,
    (6, 5): 40,
    (6, 4): 8,
    (6, 3): 1,
    # 7 星
    (7, 7): 3_200,
    (7, 6): 120,
    (7, 5): 12,
    (7, 4): 2,
    (7, 3): 1,
    # 8 星
    (8, 8): 20_000,
    (8, 7): 800,
    (8, 6): 40,
    (8, 5): 8,
    (8, 4): 1,
    (8, 0): 1,
    # 9 星
    (9, 9): 40_000,
    (9, 8): 4_000,
    (9, 7): 120,
    (9, 6): 20,
    (9, 5): 4,
    (9, 0): 1,
    # 10 星
    (10, 10): 200_000,
    (10, 9): 10_000,
    (10, 8): 1_000,
    (10, 7): 100,
    (10, 6): 10,
    (10, 5): 1,
    (10, 0): 1,
}

SUPER_NUMBER_MULTIPLIER = 48
HIGH_LOW_MULTIPLIER = 6
ODD_EVEN_MULTIPLIER = 6

BET_UNIT = 25


def calculate_prize(
    bet_type: str,
    matched_count: int,
    bet_amount: int = BET_UNIT,
    star_level: int | None = None,
    won: bool | None = None,
) -> int:
    """
    計算獎金 (NT$)。

    Parameters
    ----------
    bet_type : "basic" | "super" | "high_low" | "odd_even"
    matched_count : 命中數量 (basic 用)
    bet_amount : 投注金額 (含倍數)
    star_level : 星級 (basic 專用, 1-10)
    won : 是否中獎 (super / high_low / odd_even 用)

    Returns
    -------
    獎金金額，未中獎回傳 0
    """
    if bet_type == "basic":
        if star_level is None:
            return 0
        multiplier = BASIC_PAYOUT.get((star_level, matched_count), 0)
        return bet_amount * multiplier

    if bet_type == "super":
        if won:
            return bet_amount * SUPER_NUMBER_MULTIPLIER
        return 0

    if bet_type == "high_low":
        if won:
            return bet_amount * HIGH_LOW_MULTIPLIER
        return 0

    if bet_type == "odd_even":
        if won:
            return bet_amount * ODD_EVEN_MULTIPLIER
        return 0

    return 0
