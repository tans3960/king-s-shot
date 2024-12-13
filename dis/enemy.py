import pygame

class Enemy:
    def __init__(self, health, movement_method, movement_probability, image_path, score):
        self.health = health
        self.movement_method = movement_method
        self.movement_probability = movement_probability
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 80))  # 이미지 크기 조정
        self.score = score  # 적을 처치했을 때의 점수
        self.position = None  # 현재 위치 저장

    def draw(self, screen, position):
        """적 이미지를 지정된 위치에 렌더링"""
        screen.blit(self.image, position)

