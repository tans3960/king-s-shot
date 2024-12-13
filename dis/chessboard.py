import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
BOARD_SIZE = 8
CELL_SIZE = 80

BACKGROUND_COLOR = (32, 18, 76)
HIGHLIGHT_COLOR = (169, 169, 169)

# 이미지 로드
piece_images = {
    "chessboard": pygame.transform.scale(pygame.image.load("img/chessboard.png"), (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE))
}

# 체스판 좌표 계산 함수
def get_board_position(col, row):
    x = (SCREEN_WIDTH - BOARD_SIZE * CELL_SIZE) // 2 + col * CELL_SIZE
    y = (SCREEN_HEIGHT - BOARD_SIZE * CELL_SIZE) // 2 + row * CELL_SIZE
    return x, y

# 체스판 그리기
def draw_chessboard(screen):
    # 체스판 이미지 불러오기
    board_width = BOARD_SIZE * CELL_SIZE
    padding_x = (SCREEN_WIDTH - board_width) // 2
    padding_y = (SCREEN_HEIGHT - board_width) // 2

    screen.fill(BACKGROUND_COLOR)
    # 체스판 이미지 그리기
    chessboard_image = piece_images.get("chessboard")
    if chessboard_image:
        screen.blit(chessboard_image, (padding_x, padding_y))
    
   # kingstanding.png 이미지를 체스판 왼쪽에 그리기
    king_image = pygame.image.load("img/kingstanding.png")
    scaled_width = 320 
    scaled_height = 650
    king_image = pygame.transform.scale(king_image, (scaled_width, scaled_height))  # 크기 조정

    king_x = padding_x - scaled_width - 10  # 체스판 왼쪽으로 이동
    king_y = 250  # 중앙 정렬
    screen.blit(king_image, (king_x, king_y))
# 체스말 그리기
def draw_pieces(screen, pieces):
    for piece, (col, row) in pieces.items():
        image = piece_images.get(piece)
        if image:
            x, y = get_board_position(col, row)
            screen.blit(image, (x, y))

