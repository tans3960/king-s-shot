import random
# 능력 종류
abil = {
    "bronze": [
        {"name": "데미지 +5", "image": "img/damage_up.png", "effect": lambda game: setattr(game, "bullet_damage", game.bullet_damage + 5)},
        {"name": "탄창 내 총알 수 +2", "image": "img/magazine_up.png", "effect": lambda game: setattr(game, "max_bullets", game.max_bullets + 2)},
    ],
    "silver": [
        {"name": "데미지 +10","image": "img/damage_up2.png", "effect": lambda game: setattr(game, "bullet_damage", game.bullet_damage + 10)},
        {"name": "탄창 내 총알 수 +3","image": "img/magazine_up2.png", "effect": lambda game: setattr(game, "max_bullets", game.max_bullets + 3)},
        {"name": "적 비숍 체력 -3", "image": "img/bishop_health_down.png", "effect": lambda game: reduce_enemy_hp(game, "bishop", 10)},
        {"name": "적 나이트 체력 -3","image": "img/knight_health_down.png", "effect": lambda game: reduce_enemy_hp(game, "knight", 15)},
    ],
    "gold": [
        {"name": "데미지 +15", "image": "img/damage_up3.png", "effect": lambda game: setattr(game, "bullet_damage", game.bullet_damage + 15)},
        {"name": "폭발","image": "img/set_explosion.png", "effect": lambda game: setattr(game, "explosion", True)},
        {"name": "적 처치 시 총알 +1","image": "img/bullets_on_kill.png", "effect": lambda game: setattr(game, "bullets_on_kill", True)},
        {"name": "내 턴에 총 2번 발사", "image": "img/shots_per_turn.png", "effect": lambda game: setattr(game, "shots_per_turn", True)},
        {"name": "3턴마다 움직일 수 있는 칸 수 +1", "image": "img/move_boost_turns.png", "effect": lambda game: setattr(game, "move_boost_turns", True)},
{"name": "적 룩 체력 -4", "image": "img/rook_health_down.png", "effect": lambda game: reduce_enemy_hp(game, "rook", 15)},
        {"name": "적 퀸 체력 -3", "image": "img/queen_health_down.png", "effect": lambda game: reduce_enemy_hp(game, "queen", 10)},
    ],
    "prism": [
        {"name": "항상 움직임 +1칸", "image": "img/prism_move.png", "effect": lambda game: setattr(game, "prism_move", True)},
        {"name": "폭발 효과 강화", "image": "img/explosion_boost.png", "effect": lambda game: setattr(game, "prism_explosion", True)},
        {"name": "3턴마다 플레이어 데미지 +1", "image": "img/damage_boost_turns.png", "effect": lambda game: setattr(game, "damage_boost_turns", True)},
        {"name": "관통", "image": "img/set_penetration.png", "effect": lambda game: setattr(game, "penetration", True)}
    ]
}
# 능력 확률
abil_prob = {
    50: {"bronze": 1.0},
    150: {"bronze":0.5,"silver":0.5},
    360: {"silver": 1.0},
    610: {"gold": 0.3, "silver": 0.7},
    940: {"gold": 0.5, "silver": 0.5},  
    1230: {"gold": 0.9, "prism": 0.1},
    1580: {"gold": 0.8, "prism": 0.2},
    1940: {"gold": 0.5, "prism": 0.5},
    2500: {"gold": 0.3, "prism": 0.7}
}
def get_rand_abil(self, score, abilities, probabilities):
    """점수와 확률에 따라 활성화되지 않은 능력을 선택"""
    if score not in probabilities:
        return None

    tiers = probabilities[score]
    tier = random.choices(list(tiers.keys()), weights=list(tiers.values()), k=1)[0]
    
    # 활성화된 능력을 제외한 선택 가능한 능력 목록
    available_abilities = [
        ability for ability in abilities[tier]
        if not self.is_ability_active(ability)  # 활성화 여부 확인
    ]

    if not available_abilities:  # 선택 가능한 능력이 없으면 None 반환
        return None

    return random.choice(available_abilities)  # 활성화되지 않은 능력 중 랜덤 선택


def reduce_enemy_hp(game, enemy_type, amount):
    """특정 적의 체력을 감소"""
    for enemy, position in game.enemies:
        if enemy.movement_method == enemy_type:
            enemy.health = max(0, enemy.health - amount)
