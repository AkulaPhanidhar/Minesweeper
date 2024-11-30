# Minesweeper with Hidden Treasure

A classic Minesweeper game implemented in Python with both Graphical User Interface (GUI) and Text-based console views. This version introduces a hidden treasure feature, adding an extra layer of excitement to the traditional gameplay. Built following the Model-View-Controller (MVC) design pattern, the game ensures a clean separation of concerns, enhancing maintainability and scalability.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [GUI Mode](#gui-mode)
  - [Text Mode](#text-mode)
- [Gameplay](#gameplay)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Dual Interface:** Choose between a user-friendly GUI built with Tkinter or a straightforward Text-based console interface.
- **Hidden Treasure:** In addition to mines, a hidden treasure is randomly placed on the board. Finding the treasure results in an immediate win.
- **MVC Architecture:** Organized using the Model-View-Controller pattern for better code management and scalability.
- **Flagging Mechanism:** Right-click to flag or unflag suspected mines.
- **Timer:** Track the duration of your game.
- **Replayability:** Option to play again after a game ends.

## Requirements

- **Python 3.x**

  Ensure you have Python 3 installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

- **Tkinter**

  Tkinter is included in the standard Python distribution. If it's not installed, you can install it using your package manager.

  - **Windows:** Typically comes pre-installed with Python.
  - **macOS:** Usually included with Python.
  - **Linux:** Install using your distribution's package manager. For example:

    ```bash
    sudo apt-get install python3-tk
    ```

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/minesweeper-treasure.git
   cd minesweeper-treasure
   ```
