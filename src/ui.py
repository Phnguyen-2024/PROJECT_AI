import pygame
import math
import os
try:
    from PIL import Image
    pillow_available = True
except ImportError:
    pillow_available = False

pygame.init()
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Error initializing mixer: {e}")

WIDTH, HEIGHT = 800, 600
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TRUY TÌM KHO BÁU")
except pygame.error as e:
    print(f"Error initializing display: {e}")
    exit()

def load_gif_frames(gif_path):
    frames = []
    if not pillow_available:
        print("Pillow not installed, cannot load GIF")
        return frames
    try:
        image = Image.open(gif_path)
        for frame in range(image.n_frames):
            image.seek(frame)
            frame_surface = pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert()
            frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
            frames.append(frame_surface)
    except Exception as e:
        print(f"Không thể load ảnh nền động: {e}")
    return frames

gif_path = r"D:\Nam2_HKII\AI\PROJECT\PROJECT_AI\src\hinhnen.gif"
gif_frames = load_gif_frames(gif_path)
frame_count = len(gif_frames)
current_frame = 0
frame_timer = 0

def show_start_screen(screen):
    global current_frame, frame_timer

    try:
        # Font cho tiêu đề: Papyrus (phong cách phiêu lưu), size 40
        title_font = pygame.font.SysFont("papyrus", 40, bold=True)
        # Font cho nút: Times New Roman, size 40
        button_font = pygame.font.SysFont("timesnewroman", 40, bold=True)
        error_font = pygame.font.SysFont("timesnewroman", 30)
    except pygame.error as e:
        print(f"Error initializing fonts: {e}")
        title_font = pygame.font.Font(None, 40)
        button_font = pygame.font.Font(None, 40)
        error_font = pygame.font.Font(None, 30)

    SEA_COLOR = (0, 105, 148)
    SAND_COLOR = (255, 228, 181)
    BUTTON_COLOR = (160, 82, 45)
    BUTTON_HOVER_COLOR = (255, 215, 0)
    TEXT_COLOR = (255, 255, 255)
    ERROR_COLOR = (255, 0, 0)
    SOUND_ON_COLOR = (0, 255, 0)
    SOUND_OFF_COLOR = (255, 0, 0)
    SHADOW_COLOR = (50, 50, 50)  # Xám cho bóng
    OUTLINE_COLOR = (0, 0, 0)  # Đen cho viền

    wave_offset = 0

    sound_on = True
    music_loaded = False
    error_messages = []
    last_sound_click = 0
    SOUND_CLICK_DELAY = 200

    music_path = r"D:\Nam2_HKII\AI\PROJECT\PROJECT_AI\src\nhacnen.mp3"
    music_icon_path = r"D:\Nam2_HKII\AI\PROJECT\PROJECT_AI\src\music_icon.png"

    if not os.path.exists(music_path):
        error_messages.append(f"Music file not found: {music_path}")
        print(error_messages[-1])
    if not os.path.exists(music_icon_path):
        error_messages.append(f"Music icon not found: {music_icon_path}")
        print(error_messages[-1])

    try:
        music_icon = pygame.image.load(music_icon_path)
        music_icon = pygame.transform.scale(music_icon, (40, 40))
    except pygame.error as e:
        error_messages.append(f"Error loading music icon: {e}")
        print(error_messages[-1])
        music_icon = pygame.Surface((40, 40))
        music_icon.fill((0, 255, 255))

    try:
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            music_loaded = True
        else:
            error_messages.append(f"Music file not found: {music_path}")
            print(error_messages[-1])
    except pygame.error as e:
        error_messages.append(f"Error loading music: {e}")
        print(error_messages[-1])
        music_loaded = False
        try:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=44100, size=-16, channels=2)
        except pygame.error as e:
            print(f"Error reinitializing mixer: {e}")

    # Loại bỏ gradient nền, chỉ giữ hiệu ứng cho chữ
    title_text = "TRUY TÌM KHO BÁU"
    char_surfaces = []
    total_width = 0
    char_spacing = 2  # Khoảng cách giữa các ký tự

    for char in title_text:
        char_surface = title_font.render(char, True, (255, 255, 255))
        char_rect = char_surface.get_rect()
        temp_char_surface = pygame.Surface((char_rect.width + 4, char_rect.height + 4), pygame.SRCALPHA)

        for dx, dy in [(1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]:
            outline_char = title_font.render(char, True, OUTLINE_COLOR)
            temp_char_surface.blit(outline_char, (dx + 2, dy + 2))

        temp_char_surface.blit(char_surface, (2, 2))

        shadow_char = title_font.render(char, True, SHADOW_COLOR)
        shadow_char_surface = pygame.Surface((char_rect.width + 4, char_rect.height + 4), pygame.SRCALPHA)
        shadow_char_surface.blit(shadow_char, (5, 5))

        char_surfaces.append((temp_char_surface, shadow_char_surface))
        total_width += char_rect.width + char_spacing

    title_x_start = (WIDTH - total_width) // 2
    title_y = HEIGHT // 6

    start_button_rect = pygame.Rect(300, 460, 200, 60)
    exit_button_rect = pygame.Rect(300, 530, 200, 60)
    sound_button_rect = pygame.Rect(740, 20, 40, 40)

    clock = pygame.time.Clock()
    running = True
    title_offset = 0
    title_alpha = 255
    while running:
        mouse_pos = pygame.mouse.get_pos()
        start_color = BUTTON_HOVER_COLOR if start_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        exit_color = BUTTON_HOVER_COLOR if exit_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        sound_color = BUTTON_HOVER_COLOR if sound_button_rect.collidepoint(mouse_pos) else (SOUND_ON_COLOR if sound_on else SOUND_OFF_COLOR)

        wave_offset += 0.05
        title_alpha = 255 * (0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.003))
        title_offset += 0.05
        title_y_offset = math.sin(title_offset) * 2

        try:
            if gif_frames:
                frame_timer += 1
                if frame_timer >= 10:
                    current_frame = (current_frame + 1) % frame_count
                    frame_timer = 0
                screen.blit(gif_frames[current_frame], (0, 0))
            else:
                screen.fill(SEA_COLOR)
                pygame.draw.rect(screen, SAND_COLOR, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
                for x in range(0, WIDTH, 20):
                    y = HEIGHT // 2 + math.sin(x * 0.02 + wave_offset) * 20
                    pygame.draw.circle(screen, (135, 206, 235), (x, int(y)), 5)
        except pygame.error as e:
            print(f"Error rendering background: {e}")

        try:
            x_offset = title_x_start
            for char_surface, shadow_surface in char_surfaces:
                shadow_surface.set_alpha(title_alpha)
                screen.blit(shadow_surface, (x_offset + 3, title_y + 3 + title_y_offset))
                char_surface.set_alpha(title_alpha)
                screen.blit(char_surface, (x_offset, title_y + title_y_offset))
                x_offset += char_surface.get_width() + char_spacing
        except pygame.error as e:
            print(f"Error rendering title: {e}")

        try:
            pygame.draw.rect(screen, start_color, start_button_rect, border_radius=12)
            start_text = button_font.render("Bắt đầu", True, TEXT_COLOR)
            if start_text.get_width() == 0:
                start_text = button_font.render("Bat dau", True, TEXT_COLOR)
            screen.blit(start_text, start_text.get_rect(center=start_button_rect.center))
        except pygame.error as e:
            print(f"Error rendering start button: {e}")

        try:
            pygame.draw.rect(screen, exit_color, exit_button_rect, border_radius=12)
            exit_text = button_font.render("Thoát", True, TEXT_COLOR)
            screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))
        except pygame.error as e:
            print(f"Error rendering exit button: {e}")

        try:
            pygame.draw.rect(screen, sound_color, sound_button_rect, border_radius=5)
            screen.blit(music_icon, sound_button_rect)
            if not music_loaded:
                no_music_text = error_font.render("No music loaded", True, ERROR_COLOR)
                screen.blit(no_music_text, (sound_button_rect.x - 100, sound_button_rect.y + 40))
        except pygame.error as e:
            print(f"Error rendering sound button: {e}")

        try:
            for i, msg in enumerate(error_messages[-3:]):
                error_text = error_font.render(msg, True, ERROR_COLOR)
                error_rect = error_text.get_rect(center=(WIDTH // 2, HEIGHT - 50 - i * 30))
                screen.blit(error_text, error_rect)
        except pygame.error as e:
            print(f"Error rendering error messages: {e}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                current_time = pygame.time.get_ticks()
                if start_button_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()
                elif sound_button_rect.collidepoint(event.pos) and music_loaded and (current_time - last_sound_click > SOUND_CLICK_DELAY):
                    last_sound_click = current_time
                    sound_on = not sound_on
                    try:
                        if sound_on:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                    except pygame.error as e:
                        print(f"Error toggling music: {e}")
                        error_messages.append(f"Error toggling music: {e}")

        try:
            pygame.display.flip()
        except pygame.error as e:
            print(f"Error flipping display: {e}")
        clock.tick(60)

def show_level_complete(screen):
    global current_frame, frame_timer

    try:
        title_font = pygame.font.SysFont("papyrus", 50, bold=True)
        button_font = pygame.font.SysFont("timesnewroman", 40, bold=True)
        error_font = pygame.font.SysFont("timesnewroman", 30)
    except pygame.error as e:
        print(f"Error initializing fonts: {e}")
        title_font = pygame.font.Font(None, 50)
        button_font = pygame.font.Font(None, 40)
        error_font = pygame.font.Font(None, 30)

    SEA_COLOR = (0, 105, 148)
    SAND_COLOR = (255, 228, 181)
    BUTTON_COLOR = (160, 82, 45)
    BUTTON_HOVER_COLOR = (255, 215, 0)
    TEXT_COLOR = (255, 255, 255)
    ERROR_COLOR = (255, 0, 0)
    SHADOW_COLOR = (50, 50, 50)
    OUTLINE_COLOR = (0, 0, 0)

    wave_offset = 0
    title_text = "LEVEL COMPLETE"
    char_surfaces = []
    total_width = 0
    char_spacing = 2

    for char in title_text:
        char_surface = title_font.render(char, True, (255, 255, 255))
        char_rect = char_surface.get_rect()
        temp_char_surface = pygame.Surface((char_rect.width + 4, char_rect.height + 4), pygame.SRCALPHA)

        for dx, dy in [(1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]:
            outline_char = title_font.render(char, True, OUTLINE_COLOR)
            temp_char_surface.blit(outline_char, (dx + 2, dy + 2))

        temp_char_surface.blit(char_surface, (2, 2))

        shadow_char = title_font.render(char, True, SHADOW_COLOR)
        shadow_char_surface = pygame.Surface((char_rect.width + 4, char_rect.height + 4), pygame.SRCALPHA)
        shadow_char_surface.blit(shadow_char, (5, 5))

        char_surfaces.append((temp_char_surface, shadow_char_surface))
        total_width += char_rect.width + char_spacing

    title_x_start = (WIDTH - total_width) // 2
    title_y = HEIGHT // 6

    continue_button_rect = pygame.Rect(300, 400, 200, 60)
    exit_button_rect = pygame.Rect(300, 480, 200, 60)

    clock = pygame.time.Clock()
    running = True
    title_offset = 0
    title_alpha = 255
    while running:
        mouse_pos = pygame.mouse.get_pos()
        continue_color = BUTTON_HOVER_COLOR if continue_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        exit_color = BUTTON_HOVER_COLOR if exit_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

        wave_offset += 0.05
        title_alpha = 255 * (0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.003))
        title_offset += 0.05
        title_y_offset = math.sin(title_offset) * 2

        try:
            if gif_frames:
                frame_timer += 1
                if frame_timer >= 10:
                    current_frame = (current_frame + 1) % frame_count
                    frame_timer = 0
                screen.blit(gif_frames[current_frame], (0, 0))
            else:
                screen.fill(SEA_COLOR)
                pygame.draw.rect(screen, SAND_COLOR, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
                for x in range(0, WIDTH, 20):
                    y = HEIGHT // 2 + math.sin(x * 0.02 + wave_offset) * 20
                    pygame.draw.circle(screen, (135, 206, 235), (x, int(y)), 5)
        except pygame.error as e:
            print(f"Error rendering background: {e}")

        try:
            x_offset = title_x_start
            for char_surface, shadow_surface in char_surfaces:
                shadow_surface.set_alpha(title_alpha)
                screen.blit(shadow_surface, (x_offset + 3, title_y + 3 + title_y_offset))
                char_surface.set_alpha(title_alpha)
                screen.blit(char_surface, (x_offset, title_y + title_y_offset))
                x_offset += char_surface.get_width() + char_spacing
        except pygame.error as e:
            print(f"Error rendering title: {e}")

        try:
            pygame.draw.rect(screen, continue_color, continue_button_rect, border_radius=12)
            continue_text = button_font.render("Tiếp tục", True, TEXT_COLOR)
            screen.blit(continue_text, continue_text.get_rect(center=continue_button_rect.center))
        except pygame.error as e:
            print(f"Error rendering continue button: {e}")

        try:
            pygame.draw.rect(screen, exit_color, exit_button_rect, border_radius=12)
            exit_text = button_font.render("Thoát", True, TEXT_COLOR)
            screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))
        except pygame.error as e:
            print(f"Error rendering exit button: {e}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button_rect.collidepoint(event.pos):
                    return  # Tiếp tục sang màn tiếp theo
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()

        try:
            pygame.display.flip()
        except pygame.error as e:
            print(f"Error flipping display: {e}")
        clock.tick(60)

if __name__ == "__main__":
    show_start_screen(screen)
    pygame.quit()

# import pygame
# import math
# import os
# from game_screen import show_game_screen  # Import hàm show_game_screen từ game_screen.py

# pygame.init()
# try:
#     pygame.mixer.init()
# except pygame.error as e:
#     print(f"Error initializing mixer: {e}")

# WIDTH, HEIGHT = 800, 600
# try:
#     screen = pygame.display.set_mode((WIDTH, HEIGHT))
#     pygame.display.set_caption("TRUY TÌM KHO BÁU")
# except pygame.error as e:
#     print(f"Error initializing display: {e}")
#     exit()

# def show_start_screen(screen):
#     try:
#         # Font cho tiêu đề: Papyrus (phong cách phiêu lưu), size 40
#         title_font = pygame.font.SysFont("papyrus", 40, bold=True)
#         # Font cho nút: Times New Roman, size 40
#         button_font = pygame.font.SysFont("timesnewroman", 40, bold=True)
#         error_font = pygame.font.SysFont("timesnewroman", 30)
#     except pygame.error as e:
#         print(f"Error initializing fonts: {e}")
#         title_font = pygame.font.Font(None, 40)
#         button_font = pygame.font.Font(None, 40)
#         error_font = pygame.font.Font(None, 30)

#     SEA_COLOR = (0, 105, 148)
#     SAND_COLOR = (255, 228, 181)
#     BUTTON_COLOR = (160, 82, 45)
#     BUTTON_HOVER_COLOR = (255, 215, 0)
#     TEXT_COLOR = (255, 255, 255)
#     ERROR_COLOR = (255, 0, 0)
#     SOUND_ON_COLOR = (0, 255, 0)
#     SOUND_OFF_COLOR = (255, 0, 0)
#     SHADOW_COLOR = (50, 50, 50)  # Xám cho bóng
#     OUTLINE_COLOR = (0, 0, 0)  # Đen cho viền

#     wave_offset = 0

#     sound_on = True
#     music_loaded = False
#     error_messages = []
#     last_sound_click = 0
#     SOUND_CLICK_DELAY = 200

#     music_path = r"D:\Nam2_HKII\AI\PROJECT\PROJECT_AI\src\nhacnen.mp3"
#     music_icon_path = r"D:\Nam2_HKII\AI\PROJECT\PROJECT_AI\src\music_icon.png"

#     if not os.path.exists(music_path):
#         error_messages.append(f"Music file not found: {music_path}")
#         print(error_messages[-1])
#     if not os.path.exists(music_icon_path):
#         error_messages.append(f"Music icon not found: {music_icon_path}")
#         print(error_messages[-1])

#     try:
#         music_icon = pygame.image.load(music_icon_path)
#         music_icon = pygame.transform.scale(music_icon, (40, 40))
#     except pygame.error as e:
#         error_messages.append(f"Error loading music icon: {e}")
#         print(error_messages[-1])
#         music_icon = pygame.Surface((40, 40))
#         music_icon.fill((0, 255, 255))

#     try:
#         if os.path.exists(music_path):
#             pygame.mixer.music.load(music_path)
#             pygame.mixer.music.set_volume(0.5)
#             pygame.mixer.music.play(-1)
#             music_loaded = True
#         else:
#             error_messages.append(f"Music file not found: {music_path}")
#             print(error_messages[-1])
#     except pygame.error as e:
#         error_messages.append(f"Error loading music: {e}")
#         print(error_messages[-1])
#         music_loaded = False
#         try:
#             pygame.mixer.quit()
#             pygame.mixer.init(frequency=44100, size=-16, channels=2)
#         except pygame.error as e:
#             print(f"Error reinitializing mixer: {e}")

#     # Loại bỏ gradient nền, chỉ giữ hiệu ứng cho chữ
#     title_text = "TRUY TÌM KHO BÁU"
#     char_surfaces = []
#     total_width = 0
#     char_spacing = 2  # Khoảng cách giữa các ký tự

#     for char in title_text:
#         char_surface = title_font.render(char, True, (255, 255, 255))
#         char_rect = char_surface.get_rect()
#         temp_char_surface = pygame.Surface((char_rect.width + 4, char_rect.height + 4), pygame.SRCALPHA)

#         for dx, dy in [(1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]:
#             outline_char = title_font.render(char, True, OUTLINE_COLOR)
#             temp_char_surface.blit(outline_char, (dx + 2, dy + 2))

#         temp_char_surface.blit(char_surface, (2, 2))

#         shadow_char = title_font.render(char, True, SHADOW_COLOR)
#         shadow_char_surface = pygame.Surface((char_rect.width + 4, char_rect.height + 4), pygame.SRCALPHA)
#         shadow_char_surface.blit(shadow_char, (5, 5))

#         char_surfaces.append((temp_char_surface, shadow_char_surface))
#         total_width += char_rect.width + char_spacing

#     title_x_start = (WIDTH - total_width) // 2
#     title_y = HEIGHT // 6

#     start_button_rect = pygame.Rect(300, 460, 200, 60)
#     exit_button_rect = pygame.Rect(300, 530, 200, 60)
#     sound_button_rect = pygame.Rect(740, 20, 40, 40)

#     clock = pygame.time.Clock()
#     running = True
#     title_offset = 0
#     title_alpha = 255
#     while running:
#         mouse_pos = pygame.mouse.get_pos()
#         start_color = BUTTON_HOVER_COLOR if start_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
#         exit_color = BUTTON_HOVER_COLOR if exit_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
#         sound_color = BUTTON_HOVER_COLOR if sound_button_rect.collidepoint(mouse_pos) else (SOUND_ON_COLOR if sound_on else SOUND_OFF_COLOR)

#         wave_offset += 0.05
#         title_alpha = 255 * (0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.003))
#         title_offset += 0.05
#         title_y_offset = math.sin(title_offset) * 2

#         screen.fill(SEA_COLOR)
#         pygame.draw.rect(screen, SAND_COLOR, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
#         for x in range(0, WIDTH, 20):
#             y = HEIGHT // 2 + math.sin(x * 0.02 + wave_offset) * 20
#             pygame.draw.circle(screen, (135, 206, 235), (x, int(y)), 5)

#         try:
#             x_offset = title_x_start
#             for char_surface, shadow_surface in char_surfaces:
#                 shadow_surface.set_alpha(title_alpha)
#                 screen.blit(shadow_surface, (x_offset + 3, title_y + 3 + title_y_offset))
#                 char_surface.set_alpha(title_alpha)
#                 screen.blit(char_surface, (x_offset, title_y + title_y_offset))
#                 x_offset += char_surface.get_width() + char_spacing
#         except pygame.error as e:
#             print(f"Error rendering title: {e}")

#         try:
#             pygame.draw.rect(screen, start_color, start_button_rect, border_radius=12)
#             start_text = button_font.render("Bắt đầu", True, TEXT_COLOR)
#             if start_text.get_width() == 0:
#                 start_text = button_font.render("Bat dau", True, TEXT_COLOR)
#             screen.blit(start_text, start_text.get_rect(center=start_button_rect.center))
#         except pygame.error as e:
#             print(f"Error rendering start button: {e}")

#         try:
#             pygame.draw.rect(screen, exit_color, exit_button_rect, border_radius=12)
#             exit_text = button_font.render("Thoát", True, TEXT_COLOR)
#             screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))
#         except pygame.error as e:
#             print(f"Error rendering exit button: {e}")

#         try:
#             pygame.draw.rect(screen, sound_color, sound_button_rect, border_radius=5)
#             screen.blit(music_icon, sound_button_rect)
#             if not music_loaded:
#                 no_music_text = error_font.render("No music loaded", True, ERROR_COLOR)
#                 screen.blit(no_music_text, (sound_button_rect.x - 100, sound_button_rect.y + 40))
#         except pygame.error as e:
#             print(f"Error rendering sound button: {e}")

#         try:
#             for i, msg in enumerate(error_messages[-3:]):
#                 error_text = error_font.render(msg, True, ERROR_COLOR)
#                 error_rect = error_text.get_rect(center=(WIDTH // 2, HEIGHT - 50 - i * 30))
#                 screen.blit(error_text, error_rect)
#         except pygame.error as e:
#             print(f"Error rendering error messages: {e}")

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.mixer.music.stop()
#                 pygame.quit()
#                 exit()
#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 current_time = pygame.time.get_ticks()
#                 if start_button_rect.collidepoint(event.pos):
#                     pygame.mixer.music.stop()
#                     show_game_screen(screen)  # Chuyển sang giao diện chơi game
#                 elif exit_button_rect.collidepoint(event.pos):
#                     pygame.mixer.music.stop()
#                     pygame.quit()
#                     exit()
#                 elif sound_button_rect.collidepoint(event.pos) and music_loaded and (current_time - last_sound_click > SOUND_CLICK_DELAY):
#                     last_sound_click = current_time
#                     sound_on = not sound_on
#                     try:
#                         if sound_on:
#                             pygame.mixer.music.unpause()
#                         else:
#                             pygame.mixer.music.pause()
#                     except pygame.error as e:
#                         print(f"Error toggling music: {e}")
#                         error_messages.append(f"Error toggling music: {e}")

#         try:
#             pygame.display.flip()
#         except pygame.error as e:
#             print(f"Error flipping display: {e}")
#         clock.tick(60)

# def show_level_complete(screen):
#     try:
#         title_font = pygame.font.SysFont("papyrus", 50, bold=True)
#         button_font = pygame.font.SysFont("timesnewroman", 40, bold=True)
#         error_font = pygame.font.SysFont("timesnewroman", 30)
#     except pygame.error as e:
#         print(f"Error initializing fonts: {e}")
#         title_font = pygame.font.Font(None, 50)
#         button_font = pygame.font.Font(None, 40)
#         error_font = pygame.font.Font(None, 30)

#     SEA_COLOR = (0, 105, 148)
#     SAND_COLOR = (255, 228, 181)
#     BUTTON_COLOR = (160, 82, 45)
#     BUTTON_HOVER_COLOR = (255, 215, 0)
#     TEXT_COLOR = (255, 255, 255)
#     ERROR_COLOR = (255, 0, 0)
#     SHADOW_COLOR = (50, 50, 50)
#     OUTLINE_COLOR = (0, 0, 0)

#     wave_offset = 0
#     title_text = "LEVEL COMPLETE"
#     char_surfaces = []
#     total_width = 0
#     char_spacing = 2

#     for char in title_text:
#         char_surface = title_font.render(char, True, (255, 255, 255))
#         char_rect = char_surface.get_rect()
#         temp_char_surface = pygame.Surface((char_rect.width + 4, char_rect.height + 4), pygame.SRCALPHA)

#         for dx, dy in [(1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]:
#             outline_char = title_font.render(char, True, OUTLINE_COLOR)
#             temp_char_surface.blit(outline_char, (dx + 2, dy + 2))

#         temp_char_surface.blit(char_surface, (2, 2))

#         shadow_char = title_font.render(char, True, SHADOW_COLOR)
#         shadow_char_surface = pygame.Surface((char_rect.width + 4, char_rect.height + 4), pygame.SRCALPHA)
#         shadow_char_surface.blit(shadow_char, (5, 5))

#         char_surfaces.append((temp_char_surface, shadow_char_surface))
#         total_width += char_rect.width + char_spacing

#     title_x_start = (WIDTH - total_width) // 2
#     title_y = HEIGHT // 6

#     continue_button_rect = pygame.Rect(300, 400, 200, 60)
#     exit_button_rect = pygame.Rect(300, 480, 200, 60)

#     clock = pygame.time.Clock()
#     running = True
#     title_offset = 0
#     title_alpha = 255
#     while running:
#         mouse_pos = pygame.mouse.get_pos()
#         continue_color = BUTTON_HOVER_COLOR if continue_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
#         exit_color = BUTTON_HOVER_COLOR if exit_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

#         wave_offset += 0.05
#         title_alpha = 255 * (0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.003))
#         title_offset += 0.05
#         title_y_offset = math.sin(title_offset) * 2

#         screen.fill(SEA_COLOR)
#         pygame.draw.rect(screen, SAND_COLOR, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
#         for x in range(0, WIDTH, 20):
#             y = HEIGHT // 2 + math.sin(x * 0.02 + wave_offset) * 20
#             pygame.draw.circle(screen, (135, 206, 235), (x, int(y)), 5)

#         try:
#             x_offset = title_x_start
#             for char_surface, shadow_surface in char_surfaces:
#                 shadow_surface.set_alpha(title_alpha)
#                 screen.blit(shadow_surface, (x_offset + 3, title_y + 3 + title_y_offset))
#                 char_surface.set_alpha(title_alpha)
#                 screen.blit(char_surface, (x_offset, title_y + title_y_offset))
#                 x_offset += char_surface.get_width() + char_spacing
#         except pygame.error as e:
#             print(f"Error rendering title: {e}")

#         try:
#             pygame.draw.rect(screen, continue_color, continue_button_rect, border_radius=12)
#             continue_text = button_font.render("Tiếp tục", True, TEXT_COLOR)
#             screen.blit(continue_text, continue_text.get_rect(center=continue_button_rect.center))
#         except pygame.error as e:
#             print(f"Error rendering continue button: {e}")

#         try:
#             pygame.draw.rect(screen, exit_color, exit_button_rect, border_radius=12)
#             exit_text = button_font.render("Thoát", True, TEXT_COLOR)
#             screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))
#         except pygame.error as e:
#             print(f"Error rendering exit button: {e}")

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.mixer.music.stop()
#                 pygame.quit()
#                 exit()
#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 if continue_button_rect.collidepoint(event.pos):
#                     show_game_screen(screen)  # Chuyển sang màn chơi game
#                 elif exit_button_rect.collidepoint(event.pos):
#                     pygame.mixer.music.stop()
#                     pygame.quit()
#                     exit()

#         try:
#             pygame.display.flip()
#         except pygame.error as e:
#             print(f"Error flipping display: {e}")
#         clock.tick(60)

# if __name__ == "__main__":
#     show_start_screen(screen)
#     pygame.quit()
