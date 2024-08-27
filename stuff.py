import pygame
import pygame.midi

def list_midi_devices():
    pygame.midi.init()
    device_count = pygame.midi.get_count()
    print("Available MIDI devices:")
    for i in range(device_count):
        info = pygame.midi.get_device_info(i)
        device_type = "Output" if info[3] == 1 else "Input"
        interf, name, is_input, is_output, opened = info
        print(f"ID: {i}, Name: {name.decode()}, Type: {device_type}, Opened: {opened}")

    pygame.midi.quit()

list_midi_devices()

