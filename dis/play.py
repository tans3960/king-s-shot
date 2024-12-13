import pygame
import enemy
from chessboard import draw_chessboard, get_board_position
import setting
import math
import random
from ability import abil
from ability import abil_prob
from ability import get_rand_abil



class Bullet:
    def __init__(self, x, y, target_x, target_y, speed, damage):
        self.image = pygame.image.load("img/bulletimg.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.penetration = False  # 관통 여부
        angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self, screen_width, screen_height):
        return self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height

    def collides_with(self, enemy_position):
        enemy_x, enemy_y = enemy_position
        return enemy_x <= self.x <= enemy_x + 80 and enemy_y <= self.y <= enemy_y + 80

class PlayScreen:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.running = True
        self.clock = pygame.time.Clock()  # FPS 제어용 Clock 객체 생성
        self.target_fps = 144  # 목표 프레임 속도 (120 이상으로 설정)
        self.player_image = pygame.image.load("img/king.png")
        self.player_image = pygame.transform.scale(self.player_image, (80, 80))  # 이미지 크기 조정
        self.player_position = (4, 7)  # 체스보드 아래 중앙 위치 (열, 행)
        self.show_highlight = False  # 하이라이트 표시 여부
        self.highlight_positions = []  # 하이라이트 위치
        self.bullet_damage = 10  # 기본 데미지
        self.bullets = []  # 발사된 총알 목록
        self.max_bullets = 5  # 최대 발사 가능한 총알 수
        self.bullet_image = pygame.image.load("img/bulletimg.png")
        self.bullet_image = pygame.transform.scale(self.bullet_image, (100, 100))
        self.bullets_remaining = self.max_bullets
        self.penetration = False
        self.abil_shown= set()  # 이미 표시된 점수 저장
        self.sc_the = [50, 150, 360, 610, 940, 1230, 1580, 1940, 2500]  # 점수 기준
        self.selected_abil = []  # 선택한 능력 저장
        self.abil_slot_count = 9  # 최대 능력 칸 수

        # 3x3 그리드의 칸 좌표 정의
        self.abil_slots = [
            (900 + (i % 2) * 190, 10 + (i // 2) * 200)  # x: 900+열, y: 70+행
            for i in range(9)
        ]  
        
        self.player_turn = True

        self.explosion = False  # 폭발
        self.prism_explosion = False  # 프리즘 폭발 효과
        self.bullets_kill = False  # 적 처치 시 총알 +1

        self.move_boost_turns = False  # 이동 칸 확장 여부를 결정하는 변수
        self.move_boost_turn_count = 0  # 턴을 추적하는 카운터
        self.turn_count=0 # 턴 카운터

        self.shots_per_turn = False  # 기본 1번 발사
        self.shots_fired = 0    # 현재 턴에서 발사한 총알 수

        self.prism_move = False  # 항상 1칸더 이동

        self.prism_dam = False  # 프리즘 3턴마다 데미지+1
        self.damage_turn_count = 0        # 현재 턴 추적
        self.damage_shots_fired = 0  # 프리즘 3턴 계산 변수
        
        self.has_moved = False  # 플레이어가 이동했는지 여부
        self.turn_cooldown = 3000  # 상대 턴 대기 시간 (밀리초)
        self.last_turn_time = 0
        self.font = pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 60)  # 한글 폰트 설정
        self.enemies = []  # 적 목록
        self.score = 0  # 플레이어 점수
        self.now_stage = 0  # 현재 진행 중인 점수 단계
        # 초기 적 소환
        self.spawn_enemy()
        # 능력 관련 변수
#### 능력 관련 함수
    #능력 함수
    #준오

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



    def is_ability_active(self, ability):
        """능력이 이미 활성화되었는지 확인"""
        if ability["name"] == "폭발" and self.explosion:
            return True
        if ability["name"] == "관통" and self.penetration:
            return True
        if ability["name"] == "내 턴에 총 2번 발사" and self.shots_per_turn:
            return True
        if ability["name"] == "3턴마다 움직일 수 있는 칸 수 +1" and self.move_boost_turns:
            return True
        if ability["name"] == "폭발 효과 강화" and self.prism_explosion:
            return True
        if ability["name"] == "3턴마다 플레이어 데미지 +1" and self.damage_boost_turns:
            return True
        if ability["name"] == "항상 움직임 +1칸" and self.prism_move:
            return True
        if ability["name"] == "적 처치 시 총알 +1" and self.bullets_kill:
            return True
        return False  # 기본적으로 활성화되지 않았음


    def make_explosion(self, position):
        """폭발 효과 처리"""
        explosion_damage = self.set_explo_damage()  # 능력에 따른 폭발 데미지 계산
        for enemy, enemy_pos in self.enemies[:]:  # 적 리스트 복사본 사용
            # 주변 반경 1칸(상하좌우 및 대각선) 내 적 확인
            if abs(position[0] - enemy_pos[0]) <= 1 and abs(position[1] - enemy_pos[1]) <= 1:
                enemy.health -= explosion_damage  # 폭발 데미지를 적용
                if enemy.health <= 0:
                    # 체력이 0 이하인 적 제거
                    self.enemies.remove((enemy, enemy_pos))
                    self.score += enemy.score  # 점수 증가
    #준오
    def set_explo_damage(self):
        """능력에 따른 폭발 데미지 계산"""
        explosion_damage = 0
        if self.explosion:
            explosion_damage += 10  # 골드 폭발 효과
        if self.prism_explosion:
            explosion_damage += 15  # 프리즘 폭발 효과
        return explosion_damage
    #준오
    def ex_king_move(self):
        """킹의 이동 가능한 칸 수 증가"""
        self.highlight_positions = [
            (self.player_position[0] + dx, self.player_position[1] + dy)
            for dx in [-2, -1, 0, 1, 2] for dy in [-2, -1, 0, 1, 2]
            if (dx != 0 or dy != 0) and 0 <= self.player_position[0] + dx < 8 and 0 <= self.player_position[1] + dy < 8
        ]
    #준오    
    def three_turn(self):
        self.turn_count += 1  # 턴 증가
        if self.turn_count % 3 == 0:
            self.bullet_damage += 10  # 3턴마다 데미지 증가
            print(f"Turn {self.turn_count}: Bullet damage increased to {self.bullet_damage}")
    # 능력 선택 함수
    #준오
    def show_choice(self):
        """능력 선택 화면 표시 (2개의 능력을 보여줌)"""
        # 능력 두 개 랜덤 선택
        ability1 = self.get_rand_abil(self.score, abil, abil_prob)
        ability2 = self.get_rand_abil(self.score, abil, abil_prob)

        if not ability1 or not ability2:
            return

        # 이미지와 텍스트 설정
        ability1_image = pygame.image.load(ability1["image"])
        ability1_image = pygame.transform.scale(ability1_image, (400, 400))  # 크기 조정
        ability2_image = pygame.image.load(ability2["image"])
        ability2_image = pygame.transform.scale(ability2_image, (400, 400))  # 크기 조정

        # 능력 이미지의 화면 위치 계산
        screen_width, screen_height = self.screen.get_size()
        ability1_rect = ability1_image.get_rect(center=(screen_width // 3, screen_height // 2))
        ability2_rect = ability2_image.get_rect(center=(2 * screen_width // 3, screen_height // 2))

        # 선택된 능력 플래그
        ability_chosen = False

        while not ability_chosen:
            self.screen.fill((0, 0, 0))

            # 텍스트 렌더링
            font = pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 40)
            text = font.render("능력을 선택하세요", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_width // 2, 100))
            self.screen.blit(text, text_rect)

            # 능력 이미지 그리기
            self.screen.blit(ability1_image, ability1_rect)
            self.screen.blit(ability2_image, ability2_rect)

            # 화면 업데이트
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 왼쪽 마우스 클릭
                        mouse_pos = pygame.mouse.get_pos()
                        if ability1_rect.collidepoint(mouse_pos):
                            ability1["effect"](self)  # 능력 1 효과 적용
                            self.add_abil_img(ability1["image"])  # 선택한 능력 이미지 추가
                            ability_chosen = True
                        elif ability2_rect.collidepoint(mouse_pos):
                            ability2["effect"](self)  # 능력 2 효과 적용
                            self.add_abil_img(ability2["image"])  # 선택한 능력 이미지 추가
                            ability_chosen = True


            # 능력 선택 후 게임 상태 복구
            pygame.event.clear()
            self.player_turn = True
            self.has_moved = False
    #준오
    def add_abil_img(self, image_path):    
        """선택한 능력의 이미지를 추가"""
        if len(self.selected_abil) < len(self.abil_slots):  # 빈 칸 초과 방지
            self.selected_abil.append(image_path)
    #준오
    def draw_selected_abil(self, screen):
        """선택된 능력을 화면에 렌더링"""
        for idx, image_path in enumerate(self.selected_abil):
            slot_x, slot_y = self.abil_slots[idx]  # 각 칸의 좌표
            ability_image = pygame.image.load(image_path)  # 이미지 로드
            ability_image = pygame.transform.scale(ability_image, (220, 200))  # 크기 조정
            screen.blit(ability_image, (slot_x, slot_y))  # 칸에 이미지 렌더링
##스테이지 관련 함수
    #진재
    def spawn_enemy(self):
        """점수와 스테이지에 따라 적 소환 (무한 모드 지원)"""
        # 맨 위 두 줄에서만 소환 가능한 위치 생성
        available_positions = [(col, row) for row in [0, 1] for col in range(8)]
        random.shuffle(available_positions)  # 소환 위치를 무작위로 섞음

        # 각 열의 점유 상태를 추적
        occu_colum = set()

        def add_enemy(movement_method, base_hp, hp_bonus, movement_probability, image_path, score, count):
            """특정 적을 추가하는 함수"""
            for _ in range(count):
                while available_positions:
                    col, row = available_positions.pop()
                    # 폰이 같은 열에 소환되지 않도록 설정
                    if movement_method == "pawn" and col in occu_colum:
                        continue
                    occu_colum.add(col)
                    enemy_position = (col, row)
                    new_enemy = enemy.Enemy(
                        health=base_hp + hp_bonus,
                        movement_method=movement_method,
                        movement_probability=movement_probability,
                        image_path=image_path,
                        score=score,
                    )
                    self.enemies.append((new_enemy, enemy_position))
                    break

        # 기본 체력 설정
        base_hp_values = {
            "pawn": 10,
            "rook": 25,
            "bishop": 15,
            "knight": 20,
            "queen": 40,
        }

        # 기존 스테이지 처리 (0~10)
        if self.now_stage <= 10:
            hp_bonus = 0  # 기존 스테이지에서는 추가 체력 없음

            if self.now_stage == 0:
                add_enemy("pawn", base_hp_values["pawn"], hp_bonus, 0.9, "img/pawn.png", 10, 5)  #50
            elif self.now_stage == 1:
                add_enemy("pawn", base_hp_values["pawn"], hp_bonus, 0.9, "img/pawn.png", 10, 4)  # 40점
                add_enemy("bishop", base_hp_values["bishop"], hp_bonus, 0.7, "img/bishop.png", 30, 1) #30점
                add_enemy("knight", base_hp_values["knight"], hp_bonus, 0.8, "img/knight.png", 30, 1) # 30점  #150
            elif self.now_stage == 2:
                add_enemy("pawn", base_hp_values["pawn"], hp_bonus, 0.9, "img/pawn.png", 10, 4) #40
                add_enemy("rook", base_hp_values["rook"], hp_bonus, 0.6, "img/rook.png", 50, 1) #50
                add_enemy("bishop", base_hp_values["bishop"], hp_bonus, 0.7, "img/bishop.png", 30, 2) #60
                add_enemy("knight", base_hp_values["knight"], hp_bonus, 0.8, "img/knight.png", 30, 2) #60   #360
            elif self.now_stage == 3:
                add_enemy("pawn", base_hp_values["pawn"], hp_bonus, 0.9, "img/pawn.png", 10, 3) #30
                add_enemy("rook", base_hp_values["rook"], hp_bonus, 0.6, "img/rook.png", 50, 2) #100
                add_enemy("bishop", base_hp_values["bishop"], hp_bonus, 0.7, "img/bishop.png", 30, 2) #60
                add_enemy("knight", base_hp_values["knight"], hp_bonus, 0.8, "img/knight.png", 30, 2)# 60  #630
            elif self.now_stage == 4:
                add_enemy("pawn", base_hp_values["pawn"], hp_bonus, 0.9, "img/pawn.png", 10, 3)# 30
                add_enemy("rook", base_hp_values["rook"], hp_bonus, 0.6, "img/rook.png", 50, 3)# 150
                add_enemy("bishop", base_hp_values["bishop"], hp_bonus, 0.7, "img/bishop.png", 30, 2)  #60
                add_enemy("knight", base_hp_values["knight"], hp_bonus, 0.8, "img/knight.png", 30, 3) #90   #960
            elif self.now_stage == 5:
                add_enemy("pawn", base_hp_values["pawn"]+10, hp_bonus, 0.9, "img/pawn.png", 10, 3) #30
                add_enemy("rook", base_hp_values["rook"]+5, hp_bonus, 0.6, "img/rook.png", 50, 2) #100
                add_enemy("bishop", base_hp_values["bishop"]+5, hp_bonus, 0.7, "img/bishop.png", 30, 1) #30
                add_enemy("knight", base_hp_values["knight"]+5, hp_bonus, 0.8, "img/knight.png", 30, 1) #30
                add_enemy("queen", base_hp_values["queen"], hp_bonus, 0.5, "img/queen.png", 100, 1) #100    #1250
            elif self.now_stage == 6:
                add_enemy("pawn", base_hp_values["pawn"]+10, hp_bonus, 0.9, "img/pawn.png", 10, 3) #30
                add_enemy("rook", base_hp_values["rook"]+5, hp_bonus, 0.6, "img/rook.png", 50, 2) #100
                add_enemy("bishop", base_hp_values["bishop"]+5, hp_bonus, 0.7, "img/bishop.png", 30, 2) #60
                add_enemy("knight", base_hp_values["knight"]+5, hp_bonus, 0.8, "img/knight.png", 30, 2) #60
                add_enemy("queen", base_hp_values["queen"], hp_bonus, 0.5, "img/queen.png", 100, 1) #100  #1600
            elif self.now_stage == 7:
                add_enemy("pawn", base_hp_values["pawn"]+10, hp_bonus, 0.9, "img/pawn.png", 10, 5) #80
                add_enemy("rook", base_hp_values["rook"]+10, hp_bonus, 0.6, "img/rook.png", 50, 2) #100
                add_enemy("queen", base_hp_values["queen"], hp_bonus, 0.5, "img/queen.png", 100, 2) #200  #1980
            elif self.now_stage == 8:
                add_enemy("pawn", base_hp_values["pawn"]+10, hp_bonus, 0.9, "img/pawn.png", 10, 5) #70
                add_enemy("rook", base_hp_values["rook"]+10, hp_bonus, 0.6, "img/rook.png", 50, 3) #150
                add_enemy("bishop", base_hp_values["bishop"]+10, hp_bonus, 0.7, "img/bishop.png", 30, 2) #60
                add_enemy("knight", base_hp_values["knight"]+10, hp_bonus, 0.8, "img/knight.png", 30, 2) #60
                add_enemy("queen", base_hp_values["queen"]+5, hp_bonus, 0.5, "img/queen.png", 100, 2) #200  #2520
            elif self.now_stage == 9:
                add_enemy("pawn", base_hp_values["pawn"]+20, hp_bonus, 0.9, "img/pawn.png", 10, 5) #70
                add_enemy("rook", base_hp_values["rook"]+15, hp_bonus, 0.6, "img/rook.png", 50, 3) #150
                add_enemy("bishop", base_hp_values["bishop"]+15, hp_bonus, 0.7, "img/bishop.png", 30, 2) #60
                add_enemy("knight", base_hp_values["knight"]+15, hp_bonus, 0.8, "img/knight.png", 30, 2) #60
                add_enemy("queen", base_hp_values["queen"]+10, hp_bonus, 0.5, "img/queen.png", 100, 2) #200 #3060
            elif self.now_stage == 10:
                self.show_game_clear()
        else:
            # 무한 모드 처리
            hp_bonus = (self.now_stage - 10) // 2  # 추가 체력
            difficult_up = 1 + (self.now_stage - 10) * 0.1  # 난이도 조정
            base_count = min(12, 5 + self.now_stage - 10)  # 최대 소환 수 제한

            # 폰 소환 (항상 8개)
            add_enemy("pawn", base_hp_values["pawn"], hp_bonus, 0.9, "img/pawn.png", 10, 8)

            # 중간 기물 소환 (최소 2개)
            add_enemy("rook", base_hp_values["rook"], int(hp_bonus * difficult_up), 0.7, "img/rook.png", 50, max(2, base_count // 3))
            add_enemy("bishop", base_hp_values["bishop"], int(hp_bonus * difficult_up), 0.7, "img/bishop.png", 30, max(2, base_count // 3))
            add_enemy("knight", base_hp_values["knight"], int(hp_bonus * difficult_up), 0.8, "img/knight.png", 30, max(2, base_count // 3))

            # 퀸 소환 (난이도가 높아질수록 더 많이 소환)
            add_enemy("queen", base_hp_values["queen"], int(hp_bonus * difficult_up * 1.5), 0.6, "img/queen.png", 100, max(2, (self.now_stage - 10) // 5 + 2))

        # 턴 시작
        self.player_turn = True
## 화면 클릭 함수
    #경민 진재
    def handle_events(self, events):
        if self.player_turn:
            if self.has_moved:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        self.bullets_remaining = self.max_bullets
                        self.player_turn = False
                        self.last_turn_time = pygame.time.get_ticks()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 3:  # 오른쪽 마우스 버튼 클릭 - 총알 발사                                                   # 총 소리 재생
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            self.shoot_bullet(mouse_x, mouse_y)
                            pygame.mixer.init()
                return
            for event in events:
                if event.type == pygame.QUIT:
                    self.game.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # 설정 화면 처리
                        setting.setting_screen(self.screen)
                        while True:
                            events = pygame.event.get()
                            for ev in events:
                                if ev.type == pygame.QUIT:
                                    self.game.running = False
                                    return
                                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                    return
                            result = setting.handle_setting_events(self.screen)
                            if result == "continue":
                                return
                    elif event.key == pygame.K_r:  # R 키를 눌러 총알 재장전
                        self.bullets_remaining = self.max_bullets
                        self.player_turn = False
                        self.last_turn_time = pygame.time.get_ticks()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.has_moved:  # 왼쪽 마우스 버튼 클릭, 이동은 1회만 가능
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.handle_click(mouse_x, mouse_y)
                    elif event.button == 3:  # 오른쪽 마우스 버튼 클릭 - 총알 발사
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.shoot_bullet(mouse_x, mouse_y)
##  #경민
    def handle_click(self, mouse_x, mouse_y):
        board_x, board_y = None, None
        for row in range(8):
            for col in range(8):
                cell_x, cell_y = get_board_position(col, row)
                cell_rect = pygame.Rect(cell_x, cell_y, 80, 80)
                if cell_rect.collidepoint(mouse_x, mouse_y):
                    board_x, board_y = col, row
                    break
            if board_x is not None and board_y is not None:
                break

        if board_x is not None and board_y is not None:
            if self.show_highlight and (board_x, board_y) in self.highlight_positions:
                self.player_position = (board_x, board_y)  # 지연 시간 설정 (애니메이션 속도 조절)
                
                self.player_position = (board_x, board_y)
                self.show_highlight = False
                self.highlight_positions = []
                self.has_moved = True
            elif (board_x, board_y) == self.player_position:
                self.show_highlight = True
                self.highlight_positions = [
                    (self.player_position[0] + dx, self.player_position[1] + dy)
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                    if (dx != 0 or dy != 0) and 0 <= self.player_position[0] + dx < 8 and 0 <= self.player_position[1] + dy < 8
                ]
            else:
                self.show_highlight = False
                self.highlight_positions = []
    #준오 경민
    def shoot_bullet(self, target_x, target_y):
        if self.bullets_remaining > 0 and self.player_turn:
            if self.shots_per_turn or self.shots_fired < 1:  # 2발 가능 여부 확인
                if not self.shots_per_turn==True and self.shots_fired >= 1:
                    return  # 한 번만 발사 가능 (능력 비활성화 상태)
                if self.shots_per_turn==True and self.shots_fired >= 2:
                    return  # 두 번 발사 후 더 이상 발사 불가 (능력 활성화 상태)

                player_x, player_y = get_board_position(*self.player_position)
                bullet_x = player_x + 40  # 킹 이미지의 중앙에서 발사
                bullet_y = player_y + 40
                bullet = Bullet(bullet_x, bullet_y, target_x, target_y, speed=65, damage=self.bullet_damage) # 총알 기본 속도,데미지
                bullet.penetration = self.penetration  # 관통 설정
                self.bullets.append(bullet)
                self.bullets_remaining -= 1
                self.shots_fired += 1  # 발사 횟수 증가
                
                if self.prism_dam==True:
                    self.three_turn()

                 # 턴 종료 조건
                if (not self.shots_per_turn and self.shots_fired >= 1) or (self.shots_per_turn and self.shots_fired >= 2):
                    self.player_turn = False
                    self.shots_fired = 0  # 발사 횟수 초기화
                    
            
            self.last_turn_time = pygame.time.get_ticks()
    #진재
    def update(self):
    
        """게임 업데이트 - 적 제거 후 다음 단계 확인"""
        if not self.enemies:
            if self.now_stage < 10:
                self.now_stage += 1
                self.spawn_enemy()
            else:
                # 무한 모드에서 계속 적 소환
                self.spawn_enemy()
            self.player_turn = True  # 새로운 스테이지에서 플레이어 턴으로 시작
            
        """게임 업데이트"""
        if self.sc_the and self.score >= self.sc_the[0]:
            self.show_choice()
            self.sc_the.pop(0)  # 조건 제거
        self.turn_count += 1
        # 3턴마다 킹의 이동 범위 확장 처리
        if self.move_boost_turns ==True and self.move_boost_turn_count % 3 ==0 or self.prism_move == True:  # 항상 1칸더 이동
            self.ex_king_move()  # 3의 배수 턴에서만 확장
        else:
            self.highlight_positions = [
            (self.player_position[0] + dx, self.player_position[1] + dy)
            for dx in [-1, 0, 1] for dy in [-1, 0, 1]
            if (dx != 0 or dy != 0) and 0 <= self.player_position[0] + dx < 8 and 0 <= self.player_position[1] + dy < 8
            ]

            # 턴 종료 시 카운터 증가
        if not self.player_turn and len(self.bullets) == 0:
            self.move_boost_turn_count += 1
            
        """게임 업데이트 - 적 이동 및 플레이어 타겟팅"""
        occupied_positions = {pos for _, pos in self.enemies}  # 적들이 점유하고 있는 위치
        animations = []  # 이동할 애니메이션 정보를 저장
        animation_in_progress = False  # 애니메이션 중 여부 플래그
    
        if not self.player_turn and len(self.bullets) == 0:
            for enemy, position in self.enemies:
                possible_moves = []
    
                # 적별 이동 규칙 정의
                if enemy.movement_method == "pawn":
                    forward = (0, 1)
                    new_position = (position[0] + forward[0], position[1] + forward[1])
                    if 0 <= new_position[0] < 8 and 0 <= new_position[1] < 8 and new_position not in occupied_positions:
                        possible_moves.append(new_position)
    
                elif enemy.movement_method == "bishop":
                    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                        for i in range(1, 8):
                            new_position = (position[0] + dx * i, position[1] + dy * i)
                            if 0 <= new_position[0] < 8 and 0 <= new_position[1] < 8:
                                if new_position not in occupied_positions:
                                    possible_moves.append(new_position)
                                else:
                                    break
                            else:
                                break
                            
                elif enemy.movement_method == "knight":
                    possible_moves = [
                        (position[0] + dx, position[1] + dy)
                        for dx, dy in [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
                        if 0 <= position[0] + dx < 8 and 0 <= position[1] + dy < 8 and
                        (position[0] + dx, position[1] + dy) not in occupied_positions
                    ]
    
                elif enemy.movement_method == "rook":
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        for i in range(1, 8):
                            new_position = (position[0] + dx * i, position[1] + dy * i)
                            if 0 <= new_position[0] < 8 and 0 <= new_position[1] < 8:
                                if new_position not in occupied_positions:
                                    possible_moves.append(new_position)
                                else:
                                    break
                            else:
                                break
                            
                elif enemy.movement_method == "queen":
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                        for i in range(1, 8):
                            new_position = (position[0] + dx * i, position[1] + dy * i)
                            if 0 <= new_position[0] < 8 and 0 <= new_position[1] < 8:
                                if new_position not in occupied_positions:
                                    possible_moves.append(new_position)
                                else:
                                    break
                            else:
                                break
                            
                # 킹(플레이어)의 위치로 이동 우선 처리
                if self.player_position in possible_moves:
                    new_position = self.player_position
                elif possible_moves:
                    # 랜덤으로 이동
                    new_position = random.choice(possible_moves)
                else:
                    new_position = position

                # **폰이 마지막 줄에 도달했는지 확인**
                if enemy.movement_method == "pawn" and new_position[1] == 7:
                    self. game_over("폰이 끝에 도착해서 게임 오버")
                    return
    
                # 적 이동 후 처리
                if new_position == self.player_position:
                    # 킹의 위치로 이동 -> 게임 오버
                    self. game_over("적이 킹을 잡았습니다.")
                    return
    
                # 위치 업데이트
                if new_position != position:
                    # 이동 애니메이션 추가
                    animations.append((enemy, position, new_position))
                    occupied_positions.remove(position)
                    occupied_positions.add(new_position)
                    self.enemies = [(e, new_position if e == enemy else p) for e, p in self.enemies]
                    animation_in_progress = True
    
            # 애니메이션 처리
            if animation_in_progress:
                while animation_in_progress:
                    animation_in_progress = False
                    self.screen.fill((0, 0, 0))  # 전체 화면 초기화
                    draw_chessboard(self.screen)  # 체스보드 다시 그리기
                    self.draw_selected_abil(self.screen)  # 능력 아이콘 다시 그리기
    
                    # 킹(플레이어) 위치 그리기
                    player_x, player_y = get_board_position(*self.player_position)
                    self.screen.blit(self.player_image, (player_x, player_y))
    
                    for enemy, start_pos, end_pos in animations:
                        start_x, start_y = get_board_position(*start_pos)
                        end_x, end_y = get_board_position(*end_pos)
    
                        # 진행도 초기화
                        if not hasattr(enemy, 'progress') or enemy.progress is None:
                            enemy.progress = 0.0
    
                        progress = enemy.progress
                        if progress < 1.0:
                            animation_in_progress = True
                            progress += 0.07  # 진행 속도 조정
                            current_x = start_x + (end_x - start_x) * progress
                            current_y = start_y + (end_y - start_y) * progress
                            enemy.progress = progress
    
                            # 새 위치에서 적 이미지를 그리기
                            enemy.draw(self.screen, (current_x, current_y))
                        else:
                            # 애니메이션 완료 후 위치 고정
                            enemy.progress = None
                            self.enemies = [(e, end_pos if e == enemy else p) for e, p in self.enemies]
    
                    pygame.display.flip()
                    self.clock.tick(120)  
                    pygame.time.delay(10)  
    
                # 턴 교체
                self.player_turn = True
                self.has_moved = False


        # 총알 업데이트
        bullets_to_remove = []  # 제거할 총알 목록
        enemies_to_remove = []  # 제거할 적 목록
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen(self.screen.get_width(), self.screen.get_height()):
                self.bullets.remove(bullet)
            else:
                for enemy, position in self.enemies[:]:
                    if bullet.collides_with(get_board_position(*position)):
                        if bullet in self.bullets:  # 데미지 중복 방지
                            enemy.health -= bullet.damage
                            if enemy.health <= 0:
                                if (enemy, position) in self.enemies:
                                    self.enemies.remove((enemy, position))
                                    self.score += enemy.score
                                if self.bullets_kill:
                                    self.bullets_remaining = min(self.bullets_remaining + 1, self.max_bullets)
                                if self.explosion or self.prism_explosion:
                                    self.make_explosion(position)  # 폭발 효과 추가
                            if not bullet.penetration:  # 관통하지 않는 경우에만 총알 제거
                                self.bullets.remove(bullet)
                                break

         # 총알 및 적 제거
        for bullet in bullets_to_remove:
            if bullet in self.bullets:  # 리스트에 존재할 때만 제거
                self.bullets.remove(bullet)

        for enemy_tuple in enemies_to_remove:
            if enemy_tuple in self.enemies:  # 리스트에 존재할 때만 제거
                self.enemies.remove(enemy_tuple)
    #3명
    def draw(self, screen):
        # 체스보드 그리기
        draw_chessboard(screen)
        # 턴 표시하기
        if self.player_turn:
            turn_text = pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 50).render("플레이어 턴", True, (255, 255, 255))
        else:
            turn_text = pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 50).render("상대 턴", True, (255, 0, 0))
        score_text = pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 50).render(f"점수: {self.score}", True, (255, 255, 255))
        screen.blit(turn_text, (10, 100))
        screen.blit(score_text, (10, 150))
        # 킹이 움직일 수 있는 구역 표시
        if self.show_highlight:
            for new_col, new_row in self.highlight_positions:
                highlight_x, highlight_y = get_board_position(new_col, new_row)
                pygame.draw.circle(screen, (0, 0, 0), (highlight_x + 40, highlight_y + 40), 5)
        # 플레이어 기물 그리기
        player_x, player_y = get_board_position(*self.player_position)
        screen.blit(self.player_image, (player_x, player_y))
        # 총알 그리기
        for bullet in self.bullets:
            bullet.draw(screen)
        # 남은 총알 수 그리기
        for i in range(self.bullets_remaining):
            screen.blit(self.bullet_image, (10 + i * 35, 10))
        # 적 기물 그리기
        for enemy, position in self.enemies:
            enemy_x, enemy_y = get_board_position(*position)
            enemy.draw(screen, (enemy_x, enemy_y))
            # 적의 체력 표시
            health_text = pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 24).render(str(enemy.health), True, (255, 0, 0))
            screen.blit(health_text, (enemy_x + 20, enemy_y - 10)) 
        # 플레이어 스탯 표시 (왼쪽 하단)
        self.sh_st(screen)

        # 선택된 능력 렌더링
        self.draw_selected_abil(screen)
                 # 마우스 방향으로 선 그리기
        mouse_x, mouse_y = pygame.mouse.get_pos()
        line_start_x = player_x + 40  # 기물 중심
        line_start_y = player_y + 40
        
        # 선의 끝점을 화면 끝으로 계산
        line_end_x, line_end_y = self.calculate_line_end((line_start_x, line_start_y), (mouse_x, mouse_y))
        
        # 빨간 선 그리기
        pygame.draw.line(screen, (255, 0, 0), (line_start_x, line_start_y), (line_end_x, line_end_y), 2)
    #경민
    def calculate_line_end(self, start, mouse_pos):
        """화면 끝까지 선을 연장하기 위해 선의 끝점을 계산합니다."""
        screen_width, screen_height = self.screen.get_width(), self.screen.get_height()
        start_x, start_y = start
        mouse_x, mouse_y = mouse_pos
        dx, dy = mouse_x - start_x, mouse_y - start_y
        
        if dx == 0:  # 수직선 처리
            if dy > 0:
                return start_x, screen_height
            else:
                return start_x, 0
        
        # 기울기 계산
        slope = dy / dx
        if abs(slope) > screen_height / screen_width:  
            if dy > 0:
                y = screen_height
            else:
                y = 0
            x = start_x + (y - start_y) / slope
        else:  # 화면의 좌/우 경계와 교차
            if dx > 0:
                x = screen_width
            else:
                x = 0
            y = start_y + slope * (x - start_x)
        
        return int(x), int(y)
    #준오
    def sh_st(self, screen):
        """왼쪽 하단에 캐릭터 스탯을 표시"""
        # 텍스트 렌더링 설정
        font = pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 45)

        # 스탯 텍스트 정의
        damage_text = f"데미지: {self.bullet_damage}"  # 현재 총알 데미지
        bullet_text = f"총알 수: {self.bullets_remaining}/{self.max_bullets}"

        # 화면 크기 가져오기
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # 텍스트 렌더링
        damage_surface = font.render(damage_text, True, (255, 255, 255))
        bullet_surface = font.render(bullet_text, True, (255, 255, 255))

        # 위치 계산 (왼쪽 하단)
        damage_x, damage_y = 10, screen_height - 540  
        bullet_x, bullet_y = 10, screen_height - 490

        # 텍스트 화면에 그리기
        screen.blit(damage_surface, (damage_x, damage_y))
        screen.blit(bullet_surface, (bullet_x, bullet_y))
    #진재 경민
    def  game_over(self, message="게임 오버"):
        """게임 오버 화면 표시"""
        self.screen.fill((0, 0, 0))  # 화면 초기화
        over_txt = self.font.render(message, True, (255, 0, 0))  # 메시지를 렌더링
        self.screen.blit(
            over_txt,
            (
                self.screen.get_width() // 2 - over_txt.get_width() // 2,
                self.screen.get_height() // 2 - over_txt.get_height() // 2,
            ),
        )
        pygame.display.flip()
        pygame.time.delay(5000)  # 게임 오버 화면 유지

        # 초기 화면으로 돌아가기
        from intro import IntroScreen
        self.game.change_screen(IntroScreen(self.game))
    #진재
    def show_game_clear(self):
        """게임 클리어 후 선택 화면 표시"""
        self.screen.fill((0, 0, 0)) 
        clear_txt = self.font.render("게임을 클리어했습니다!", True, (255, 255, 255))
        self.screen.blit(clear_txt, 
                        (self.screen.get_width() // 2 - clear_txt.get_width() // 2, 
                        self.screen.get_height() // 2 - clear_txt.get_height() // 2))

        # 버튼 텍스트와 위치 설정
        btn_font= pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 40)
        quit_btn_txt = btn_font.render("종료하기", True, (255, 0, 0))
        continue_btn_txt = btn_font.render("계속하기", True, (0, 255, 0))

        quit_btn_rect = quit_btn_txt.get_rect(center=(self.screen.get_width() // 3, self.screen.get_height() * 3 // 4))
        continue_btn_rect = continue_btn_txt.get_rect(center=(self.screen.get_width() * 2 // 3, self.screen.get_height() * 3 // 4))

        self.screen.blit(quit_btn_txt, quit_btn_rect.topleft)
        self.screen.blit(continue_btn_txt, continue_btn_rect.topleft)
        pygame.display.flip()

        wait_choice = True
        while wait_choice:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 왼쪽 클릭
                        mouse_pos = pygame.mouse.get_pos()
                        if quit_btn_rect.collidepoint(mouse_pos):
                            # 종료하기 버튼 클릭
                            vic = pygame.image.load("img/end.png")  # 이미지 파일 경로
                            vic = pygame.transform.scale(vic, (self.screen.get_width(), self.screen.get_height()))  # 화면 크기에 맞게 조정
                            self.screen.blit(vic, (0, 0))  # 이미지를 화면에 표시
                            pygame.display.flip()
                            pygame.time.delay(1500)  
                            from intro import IntroScreen
                            self.game.change_screen(IntroScreen(self.game))
                            wait_choice = False
                        elif continue_btn_rect.collidepoint(mouse_pos):
                            # 계속하기 버튼 클릭
                            self.start_infint()  # 무한 모드 시작
                            wait_choice = False
    #진재
    def start_infint(self):
        """무한 모드 시작"""
        self.now_stage = 11  # 무한 모드의 첫 스테이지 번호
        self.player_turn = True
        self.spawn_enemy()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.change_screen(PlayScreen(game))
    game.run()
