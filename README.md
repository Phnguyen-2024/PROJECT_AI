# Pygame Map Project

## Overview
This project is a simple Pygame application that generates a visually appealing and randomly generated tile map. The map consists of various tile types, including grass, dirt, trees, and water. The application serves as a foundation for creating more complex games or simulations using tile-based graphics.

## Project Structure
```
pygame-map-project/
│
├── assets/
│   ├── map/
│   │   ├── grass.png
│   │   ├── dirt.png
│   │   ├── tree.png
│   │   ├── water_16px.png
│   │   ├── treasure.png
│   ├── character/
│       ├── blocky.png
│
├── src/
│   ├── [main.py](http://_vscodecontentref_/1)               # Tệp chính để chạy trò chơi
│   ├── game.py               # Logic chính của trò chơi
│   ├── player.py             # Quản lý nhân vật
│   ├── map_generator.py      # Sinh bản đồ ngẫu nhiên
│   ├── utils.py              # Các hàm tiện ích
│   ├── ui.py                 # Quản lý giao diện người dùng
```

## Files Description

- **src/main.py**: The entry point of the application. It initializes Pygame, sets up the display, and contains the main game loop that handles events and rendering.

- **src/map_generator.py**: Contains functions to generate a random tilemap for the game. It exports a function `generate_random_map` that creates a 2D list representing the map layout using different tile types.

- **src/utils.py**: Includes utility functions that assist with loading images and scaling them for display. It exports functions like `load_image` which loads and scales images based on the specified tile size.

- **assets/map/dirt.png**: Image file representing dirt tiles used in the map.

- **assets/map/grass.png**: Image file representing grass tiles used in the map.

- **assets/map/tree.png**: Image file representing tree tiles used in the map.

- **assets/map/water_16px.png**: Image file representing water tiles used in the map.

## Setup Instructions
1. Ensure you have Python and Pygame installed on your system.
2. Clone this repository or download the project files.
3. Navigate to the project directory in your terminal.
4. Run the application using the command:
   ```
   python src/main.py
   ```

## Features
- Randomly generated tile maps with different terrain types.
- Full-screen interface for an immersive experience.
- Easy to extend and modify for additional features or game mechanics.

## License
This project is open-source and available for modification and distribution under the MIT License.