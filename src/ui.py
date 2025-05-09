import pygame

def show_start_screen(screen):
    font = pygame.font.Font(None, 74)
    title_text = font.render("Island Treasure Hunt", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))

    button_font = pygame.font.Font(None, 50)
    button_text = button_font.render("Start Game", True, (0, 0, 0))
    button_rect = pygame.Rect(300, 400, 200, 60)
    button_text_rect = button_text.get_rect(center=button_rect.center)

    running = True

    while running:
        screen.fill((0, 128, 128))
        screen.blit(title_text, title_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect)
        screen.blit(button_text, button_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    running = False

        pygame.display.flip()

def show_level_complete(screen):
    font = pygame.font.Font(None, 74)
    text = font.render("Level Complete! Congrats!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))

    button_font = pygame.font.Font(None, 50)

    # Nút "Thoát"
    quit_text = button_font.render("Exit", True, (0, 0, 0))
    quit_button_rect = pygame.Rect(200, 400, 200, 60)
    quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)

    # Nút "Tiếp tục"
    continue_text = button_font.render("Continue", True, (0, 0, 0))
    continue_button_rect = pygame.Rect(400, 400, 200, 60)
    continue_text_rect = continue_text.get_rect(center=continue_button_rect.center)

    running = True

    while running:
        screen.fill((0, 128, 128))
        screen.blit(text, text_rect)

        # Vẽ nút "Thoát"
        pygame.draw.rect(screen, (255, 255, 255), quit_button_rect)
        screen.blit(quit_text, quit_text_rect)

        # Vẽ nút "Tiếp tục"
        pygame.draw.rect(screen, (255, 255, 255), continue_button_rect)
        screen.blit(continue_text, continue_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"  # Báo hiệu cần thoát chương trình
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button_rect.collidepoint(event.pos):
                    return "QUIT"  # Báo hiệu cần thoát chương trình
                elif continue_button_rect.collidepoint(event.pos):
                    return "CONTINUE"  # Báo hiệu tiếp tục trò chơi

        pygame.display.flip()

def show_thank_you(screen):
    font = pygame.font.Font(None, 74)
    text = font.render("Thank you for playing!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    running = True

    while running:
        screen.fill((0, 128, 128))
        screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # Thoát khỏi hàm và kết thúc chương trình

        pygame.display.flip()