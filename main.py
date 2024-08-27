import pygame
import pygame.midi
import random

def init_pygame():
    pygame.init()
    pygame.midi.init()

def setup_midi():
    return pygame.midi.Output(1)

def create_screen():
    screen_width = 800
    screen_height = 400
    return pygame.display.set_mode([screen_width, screen_height])

def generate_chord(num_notes=2):
    notes = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]
    return random.sample(notes, num_notes)

def play_individual_notes_and_chord(midi_out, chord):
    sorted_chord = sorted(chord)  # Sort the chord to play the lower note first
    for note in sorted_chord:
        midi_out.note_on(note, 127)
        pygame.time.wait(500)
        midi_out.note_off(note, 127)
    pygame.time.wait(500)
    play_chord(midi_out, chord)

def play_chord(midi_out, chord, delay=1000):
    for _ in range(3):  # Play the chord 3 times
        for note in chord:
            midi_out.note_on(note, 127)
        pygame.time.wait(delay)
        for note in chord:
            midi_out.note_off(note, 127)
    pygame.time.wait(delay)

def midi_to_note_name(midi_note):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return note_names[midi_note % 12] + str((midi_note // 12) - 1)

def draw_piano(screen, offset_y):
    white = (255, 255, 255)
    black = (0, 0, 0)
    white_key_width = 100
    black_key_width = 50
    black_key_height = 150

    # Draw white keys
    for i in range(8):
        pygame.draw.rect(screen, white, [i * white_key_width, offset_y, white_key_width, 300])
        pygame.draw.line(screen, black, [i * white_key_width, offset_y], [i * white_key_width, 300 + offset_y], 1)

    # Draw black keys
    black_key_positions = [70, 170, 370, 470, 570]
    for pos in black_key_positions:
        pygame.draw.rect(screen, black, [pos, offset_y, black_key_width, black_key_height])

def get_note_from_position(x, y):
    white_keys = [60, 62, 64, 65, 67, 69, 71, 72]
    black_keys = {(70, 120): 61, (170, 220): 63, (370, 420): 66, (470, 520): 68, (570, 620): 70}

    if y <= 150:  # Black keys area
        for key_range, note in black_keys.items():
            if key_range[0] < x < key_range[1]:
                return note

    return white_keys[x // 100] if x // 100 < len(white_keys) else None

def draw_button(screen, text, position, size):
    font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(position, size)
    pygame.draw.rect(screen, (200, 200, 200), button_rect)
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return button_rect

def cover_page(screen):
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 48)  # Smaller font size
    title_text = font.render("Chord Recognizer", True, (0, 0, 0))
    screen.blit(title_text, (100, 50))

    buttons = {
        "Single Note": (100, 150, 250, 40),  # Longer rectangle
        "Two Notes": (360, 150, 250, 40),
        "Three Notes": (100, 200, 250, 40),
        "Four Notes": (360, 200, 250, 40),
    }

    for text, rect in buttons.items():
        pygame.draw.rect(screen, (200, 200, 200), rect)
        button_text = font.render(text, True, (0, 0, 0))
        screen.blit(button_text, (rect[0] + 10, rect[1] + 5))

    pygame.display.flip()
    return buttons

def main(screen, midi_out):
    buttons = cover_page(screen)
    mode_selected = False
    num_notes_in_chord = 2

    while not mode_selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for text, rect in buttons.items():
                    if pygame.Rect(rect).collidepoint(x, y):
                        if text == "Single Note":
                            num_notes_in_chord = 1
                        elif text == "Two Notes":
                            num_notes_in_chord = 2
                        elif text == "Three Notes":
                            num_notes_in_chord = 3
                        elif text == "Four Notes":
                            num_notes_in_chord = 4
                        mode_selected = True
                        break

    def refresh_screen():
        screen.fill((255, 255, 255))
        draw_piano(screen, 100)
        play_again_button = draw_button(screen, "Play Again", (600, 10), (100, 30))
        next_button = draw_button(screen, "Next", (710, 10), (80, 30))
        recall_button = draw_button(screen, "Recall", (600, 50), (95, 30))
        home_button = draw_button(screen, "Home", (705, 50), (95, 30))  # New Home button
        return play_again_button, next_button, recall_button, home_button

    play_again_button, next_button, recall_button, home_button = refresh_screen()
    pygame.display.flip()

    chord = generate_chord(num_notes_in_chord)
    play_chord(midi_out, chord)  # Initial chord play

    correct_answers = 0
    total_trials = 0

    def draw_notes_feedback_and_counter():
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, 580, 90))
        note_text = ' '.join(midi_to_note_name(note) for note in sorted(user_notes))
        font = pygame.font.Font(None, 36)
        text_surf = font.render(note_text, True, (0, 0, 0))
        screen.blit(text_surf, (10, 10))

        if len(user_notes) == num_notes_in_chord:
            is_correct = set(user_notes) == set(chord)
            correct_text = "Correct!" if is_correct else f"Incorrect! Correct: {' '.join(midi_to_note_name(note) for note in sorted(chord))}"
            correct_surf = font.render(correct_text, True, (0, 255, 0) if is_correct else (255, 0, 0))
            screen.blit(correct_surf, (10, 40))

            nonlocal correct_answers, total_trials
            if is_correct:
                correct_answers += 1
            total_trials += 1

        counter_text = f"{correct_answers}/{total_trials}"
        counter_surf = font.render(counter_text, True, (0, 0, 0))
        screen.blit(counter_surf, (500, 10))

        pygame.display.flip()

    clock = pygame.time.Clock()
    user_notes = []
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if play_again_button.collidepoint(x, y):
                    play_individual_notes_and_chord(midi_out, chord)

                elif next_button.collidepoint(x, y):
                    user_notes = []
                    chord = generate_chord(num_notes_in_chord)
                    play_chord(midi_out, chord)
                    play_again_button, next_button, recall_button, home_button = refresh_screen()

                elif recall_button.collidepoint(x, y) and user_notes:
                    user_notes.pop()
                    draw_notes_feedback_and_counter()

                elif home_button.collidepoint(x, y):
                    return  # Return from main to restart the game

                if y > 100:
                    note_midi = get_note_from_position(x, y - 100)
                    if note_midi is not None and len(user_notes) < num_notes_in_chord:
                        midi_out.note_on(note_midi, 127)
                        pygame.time.wait(500)
                        midi_out.note_off(note_midi, 127)
                        user_notes.append(note_midi)
                        draw_notes_feedback_and_counter()

        clock.tick(30)

def run_application():
    init_pygame()
    midi_out = setup_midi()
    screen = create_screen()

    running = True
    while running:
        result = main(screen, midi_out)
        if result == 'quit':
            running = False

    midi_out.close()
    pygame.midi.quit()
    pygame.quit()

if __name__ == "__main__":
    run_application()
