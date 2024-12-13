#음악 관련 파일 여기서 노래 다 넣을려고 함
import pygame
import os

pygame.init()

# 음악 파일 경로
def game_music(music_file="bgm.ogg",volume=0.2):
    """음악 시작"""
    music_path = os.path.join(os.path.dirname(__file__), music_file)
    
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(volume)  
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop() 
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(volume) 
        pygame.mixer.music.play(-1)

def stop_music():
    """음악 멈춤"""
    pygame.mixer.music.stop()
