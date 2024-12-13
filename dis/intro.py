import pygame
from howto import HowToScreen
from play import PlayScreen
import music

class IntroScreen:
    def __init__(self, game):
        self.game = game
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 800

        # 배경 이미지
        self.back = pygame.image.load("img/back.png")
        
        # 폰트 설정
        self.font = pygame.font.Font("font/PF스타더스트 3.0 ExtraBold.ttf", 50)

        # 버튼 텍스트 및 초기 색상
        self.start_text = "게임 시작"
        self.how = "게임 방법"
        self.exit_text = "나가기"
        self.main_color = (35,1,149)  # 기본 색상
        self.two_color = (255, 0, 0)  # 호버 색상
        
        # 버튼 위치 설정
        self.start_button_rect = pygame.Rect(0, 0, 300, 70)
        self.start_button_rect.center = (240,600)
        
        self.how_button_rect = pygame.Rect(0, 0, 300, 70)
        self.how_button_rect.center = (640, 600)
        
        self.exit_button_rect = pygame.Rect(0, 0, 300, 70)
        self.exit_button_rect.center = (1040, 600)

        # 버튼 상태
        self.start_button_two = False
        self.how_two = False
        self.exit_button_two = False

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()

        # 올리는 상태 업데이트
        self.start_button_two = self.start_button_rect.collidepoint(mouse_pos)
        self.how_two = self.how_button_rect.collidepoint(mouse_pos)
        self.exit_button_two = self.exit_button_rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button_two:
                    self.show_intro_images()  # 이미지를 먼저 보여줌
                    self.game.change_screen(PlayScreen(self.game))  # PlayScreen으로 전환
                    music.stop_music()
                    music.game_music("bgm.ogg")
                elif self.how_two:
                    self.game.change_screen(HowToScreen(self.game))
                elif self.exit_button_two:
                    self.game.running = False
#인트로
    def show_intro_images(self):
        """5장의 이미지를 차례대로 표시하는 함수"""
        image_paths = [f"img/intro_{i}.png" for i in range(1, 3)]
        for path in image_paths:
            image = pygame.image.load(path)
            image = pygame.transform.scale(image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.game.screen.blit(image, (0, 0))
            pygame.display.flip()
            pygame.time.wait(1500)  # 각 이미지를 1.5초 동안 표시

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.back, (0, 0))
        
        # 버튼 텍스트 렌더링 (호버 상태에 따라 색상 변경)
        start_color = self.two_color if self.start_button_two else self.main_color
        how_to_play_color = self.two_color if self.how_two else self.main_color
        exit_color = self.two_color if self.exit_button_two else self.main_color

        start_text_surface = self.font.render(self.start_text, True, start_color)
        how_surface = self.font.render(self.how, True, how_to_play_color)
        exit_text_surface = self.font.render(self.exit_text, True, exit_color)

        # 텍스트 중앙 정렬로 그리기
        screen.blit(start_text_surface, start_text_surface.get_rect(center=self.start_button_rect.center))
        screen.blit(how_surface, how_surface.get_rect(center=self.how_button_rect.center))
        screen.blit(exit_text_surface, exit_text_surface.get_rect(center=self.exit_button_rect.center))
