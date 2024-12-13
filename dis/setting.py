#esc 누룰 떄 나오는 설정 아직 다 안만듬 그거 제외하고도 내부적 셋팅값도 다 넣었었음
import pygame
import os
import music  

# 화면, 색상
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
BOARD_SIZE = 8  # 체스판 크기
CELL_SIZE = 80  # 각 칸의 크기
WHITE = (255, 255, 255) 
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
RED = (255, 0 , 0)

FONT_PATH = os.path.join("font", "Maplestory Bold.ttf")

# 설정
settings = {
    "sound": True,
    "music": True,
}

# 클릭 영역 변수
clickable_areas = {}
last_click_time = 0
click_delay = 200  # 클릭 딜레이

# 설정 화면
def setting_screen(screen):
    font = pygame.font.Font(FONT_PATH, 60)
    screen_width, screen_height = pygame.display.get_surface().get_size()
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    music_text = font.render(f"음악: {'켜짐' if settings['music'] else '꺼짐'}", True, WHITE)
    exit_text = font.render("게임 나가기", True, WHITE)
    continue_text = font.render("ESC를 눌러 계속", True, WHITE)

    music_rect = music_text.get_rect(center=(screen_width // 2, screen_height // 4 - 100 + 80))
    exit_rect = exit_text.get_rect(center=(screen_width // 2, music_rect.bottom + 80))
    continue_rect = continue_text.get_rect(center=(screen_width // 2, exit_rect.bottom + 80))

    clickable_areas["music"] = music_rect
    clickable_areas["exit"] = exit_rect
    clickable_areas["continue"] = continue_rect

    # 텍스트 표시
    for key, rect in clickable_areas.items():
        pygame.draw.rect(screen, GRAY, rect, 2)
    
    screen.blit(music_text, music_rect)
    screen.blit(exit_text, exit_rect)
    screen.blit(continue_text, continue_rect)

    pygame.display.flip()

# 소리, 음악 토글
def toggle_music():
    settings["music"] = not settings["music"]
    if settings["music"]:
        music.start_music()  # 음악 켜기
    else:
        music.stop_music()   # 음악 끄기

# 클릭 이벤트 처리
def handle_setting_events(screen):
    global last_click_time  
    current_time = pygame.time.get_ticks() 
    if current_time - last_click_time < click_delay:
        return None 

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:  # 마우스 왼쪽 클릭
        for key, rect in clickable_areas.items():
            if rect.collidepoint(mouse_x, mouse_y):
                if key == "music":
                    toggle_music()
                    last_click_time = current_time
                elif key == "exit":
                    last_click_time = current_time
                    os.execvp("python", ["python", "dis/intro.py"])
                elif key == "continue":
                    last_click_time = current_time
                    return "continue"

    return None
