import pygame
import music

class HowToScreen:
    def __init__(self, game):
        self.game = game
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 800
        self.BACKGROUND_COLOR = (50, 100, 150)  # 배경색 설정
        self.WHITE = (255, 255, 255)  # 흰색 정의
        self.FONT_PATH = "font/PF스타더스트 3.0 ExtraBold.ttf"  # 폰트 경로
        self.font = pygame.font.Font(self.FONT_PATH, 50)  # 폰트 크기 조정

        # 단계별 설명 - \n 기준으로 줄바꿈 적용
        self.how_to_play_text = [
            ["1단계: 체스 킹이 움직이고", "총을 쏘거나 장전 하며 게임을 진행한다."],
            ["2단계: 총알을 쏘면", "상대턴으로 넘어간다."],
            ["3단계: 상대 기물에게 잡히면", "게임이 종료된다."],
            ["4단계: 한 스테이지가 종료되면", "능력을 선택하여 얻을 수 있다."],
            ["5단계: 10스테이지를 끝내면", "클리어 문구가 뜨고", "무한모드가 시작된다."]
        ]

        # 단계 이미지 불러오기
        from imggif import how_images
        self.step_images = [pygame.image.load(img_path) for img_path in how_images]
        self.step_images = [pygame.transform.scale(img, (500, 500)) for img in self.step_images]

        self.current_step = 0  # 현재 단계 초기화

        # 화살표 버튼
        self.arrow_size = 50
        self.left_arrow = pygame.Rect(10, self.SCREEN_HEIGHT // 2 - self.arrow_size // 2, self.arrow_size, self.arrow_size)
        self.right_arrow = pygame.Rect(1220, self.SCREEN_HEIGHT // 2 - self.arrow_size // 2, self.arrow_size, self.arrow_size)

        # 나가기 버튼
        self.howto_exit = pygame.image.load("img/bulletimg.png")
        self.howto_exit = pygame.transform.scale(self.howto_exit, (300, 70))
        self.howto_exit_rect = self.howto_exit.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 100))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.left_arrow.collidepoint(event.pos) and self.current_step > 0:
                    self.current_step -= 1  # 왼쪽 화살표 클릭 시 이전 단계로 이동
                elif self.right_arrow.collidepoint(event.pos) and self.current_step < len(self.how_to_play_text) - 1:
                    self.current_step += 1  # 오른쪽 화살표 클릭 시 다음 단계로 이동
                elif self.howto_exit_rect.collidepoint(event.pos):
                    from intro import IntroScreen
                    self.game.change_screen(IntroScreen(self.game))  # 나가기 버튼 클릭 시 인트로 화면으로 이동

    def update(self):
        pass  # 업데이트 로직 필요 시 구현 가능

    def draw(self, screen):
        screen.fill(self.BACKGROUND_COLOR)  # 배경색 설정

        # 현재 단계 이미지 표시
        image_rect = self.step_images[self.current_step].get_rect(center=(self.SCREEN_WIDTH // 4, self.SCREEN_HEIGHT // 2))
        screen.blit(self.step_images[self.current_step], image_rect)

        # 현재 단계 텍스트 표시
        y_offset = self.SCREEN_HEIGHT // 2 - 50  # 텍스트 초기 Y 좌표
        for line in self.how_to_play_text[self.current_step]:
            text_surface = self.font.render(line, True, self.WHITE)
            text_rect = text_surface.get_rect(topleft=(self.SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 50  # 각 줄 간격 조정

        # 나가기 버튼 그리기
        screen.blit(self.howto_exit, self.howto_exit_rect)

        # 화살표 그리기 (왼쪽 화살표)
        pygame.draw.polygon(screen, self.WHITE, [
            (self.left_arrow.left, self.left_arrow.centery),
            (self.left_arrow.right, self.left_arrow.top),
            (self.left_arrow.right, self.left_arrow.bottom)
        ])

        # 화살표 그리기 (오른쪽 화살표)
        pygame.draw.polygon(screen, self.WHITE, [
            (self.right_arrow.right, self.right_arrow.centery),
            (self.right_arrow.left, self.right_arrow.top),
            (self.right_arrow.left, self.right_arrow.bottom)
        ])

        pygame.display.flip()  # 화면 업데이트