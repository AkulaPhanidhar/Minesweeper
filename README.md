# Minesweeper with Hidden Treasure

## Table of Contents

1. [Introduction](#introduction)
2. [Objectives](#objectives)
3. [Features](#features)
4. [Architecture](#architecture)
   - [Model-View-Controller (MVC) Pattern](#model-view-controller-mvc-pattern)
   - [Class Overview](#class-overview)
5. [Design Principles](#design-principles)
   - [Design by Contract (DBC)](#design-by-contract-dbc)
6. [Testing Methodologies](#testing-methodologies)
   - [Testing Mode with CSV Board Loading](#testing-mode-with-csv-board-loading)
   - [Validation Rules](#validation-rules)
   - [Sample CSV Files](#sample-csv-files)
7. [Installation](#installation)
8. [Usage](#usage)
   - [Selecting Game Level](#selecting-game-level)
   - [Testing Mode](#testing-mode)
     - [Valid CSV Files](#valid-csv-files)
     - [Invalid CSV Files](#invalid-csv-files)
   - [GUI Mode](#gui-mode)
   - [Text Mode](#text-mode)
9. [Gameplay Mechanics](#gameplay-mechanics)
10. [Challenges and Solutions](#challenges-and-solutions)
11. [Future Work](#future-work)
12. [Conclusion](#conclusion)
13. [References](#references)

---

## Introduction

**Minesweeper with Hidden Treasure** is an enhanced version of the classic Minesweeper game implemented in Python. This project introduces a hidden treasure feature, adding an additional layer of excitement to the traditional gameplay. The game offers both a Graphical User Interface (GUI) built with Tkinter and a Text-based console interface, catering to different user preferences. Adhering to the Model-View-Controller (MVC) design pattern, the game ensures a clean separation of concerns, promoting maintainability and scalability.

---

## Objectives

- **Enhance Gameplay**: Introduce a hidden treasure alongside mines to provide an immediate win condition.
- **Dual Interfaces**: Offer both GUI and Text-based console views to accommodate various user preferences.
- **Robust Architecture**: Implement the MVC design pattern to maintain a clear separation between the game's logic, interface, and control mechanisms.
- **Testing Capabilities**: Allow loading predefined game boards via CSV files to facilitate thorough testing and ensure game integrity.
- **Code Reliability**: Incorporate Design by Contract (DBC) principles to specify method preconditions and postconditions, enhancing code reliability and maintainability.

---

## Features

- **Dual Interface**: Users can choose between a user-friendly GUI built with Tkinter or a straightforward Text-based console interface.
- **Hidden Treasure**: Besides mines, a hidden treasure is randomly placed on the board. Finding the treasure results in an immediate win.
- **MVC Architecture**: Organized using the Model-View-Controller pattern for better code management and scalability.
- **Flagging Mechanism**: Right-click (GUI) or input `f x y` (Text) to flag or unflag suspected mines.
- **Timer**: Track the duration of your game.
- **Replayability**: Option to play again after a game ends.
- **Testing Mode**: Load predefined game boards from CSV files to test specific scenarios and ensure game integrity.
- **Design by Contract (DBC)**: Methods include `Requires:` and `Ensures:` annotations to specify preconditions and postconditions, enhancing code reliability.

---

## Architecture

### Model-View-Controller (MVC) Pattern

The game is structured following the **Model-View-Controller (MVC)** design pattern, which divides the application into three interconnected components:

1. **Model**: Manages the game's data and logic. It maintains the state of the board, including the placement of mines and treasures, and handles the game's rules.

2. **View**: Handles the presentation layer. Depending on the user's choice, it renders either the GUI or Text-based console interface, displaying the current state of the game and interacting with the user.

3. **Controller**: Acts as an intermediary between the Model and the View. It processes user inputs, updates the Model accordingly, and instructs the View to refresh the display based on the Model's state.

### Class Overview

- **Cell**: Represents each cell on the game board. Attributes include position coordinates, mine status, flag status, reveal status, number of adjacent mines, and treasure status.

- **GameModel**: Encapsulates the game's data and logic. Responsibilities include initializing the board, placing mines and treasures, calculating adjacent mines, and handling game state updates.

- **GameController**: Processes user inputs, updates the GameModel, and coordinates with the View to reflect changes.

- **GUIView**: Implements the graphical interface using Tkinter. Handles user interactions like clicks and updates the visual representation of the board.

- **TextView**: Implements the console-based interface. Processes textual commands to reveal or flag cells and displays the board state in the console.

---

## Design Principles

### Design by Contract (DBC)

**Design by Contract (DBC)** is a methodology where software designers define precise and verifiable interface specifications for software components, which extend the ordinary definition of abstract data types with preconditions, postconditions, and invariants.

In this project, each method includes `Requires:` and `Ensures:` annotations to specify:

- **Requires**: Preconditions that must be true before the method is executed.
- **Ensures**: Postconditions that must be true after the method has executed.

This approach enhances code reliability by clearly defining method expectations and guarantees, making the codebase easier to understand, maintain, and debug.

**Example:**

```python
def on_click(self, x, y):
    """
    Requires:
        - x and y are valid cell coordinates.
        - The cell at (x, y) is not already revealed or flagged.
    Ensures:
        - Reveals the cell.
        - If the cell is a mine, triggers game over with a loss.
        - If the cell has a treasure, triggers game over with a win.
        - If the cell has zero adjacent mines, recursively reveals adjacent cells.
        - Updates the view accordingly.
        - Checks for a win condition.
    """
    # Method implementation...
```

---

## Testing Methodologies

### Testing Mode with CSV Board Loading

To facilitate thorough testing and ensure the game's integrity, a **Testing Mode** is implemented. This mode allows users to load predefined game boards from CSV files, enabling the simulation of specific scenarios without relying on random board generation.

### Validation Rules

When loading a CSV file for Testing Mode, the game validates the board based on the following rules:

1. **Format**:

   - The CSV file must contain exactly **8 rows** and **8 columns**.
   - Each cell must contain only `0`, `1`, or `2`, separated by commas.

2. **Mines (`1`)**:

   - **Total Mines**: Exactly **10 mines** must be present.
   - **Row and Column Mines**: Each row and each column must contain **at least one mine**.
   - **Main Diagonal Mines**: Only **one mine** should be placed on the main diagonal (where row index equals column index).
   - **Adjacent Mines**: There must be **exactly one pair** of adjacent mines, either horizontally or vertically.

3. **Treasures (`2`)**:
   - **Total Treasures**: At least **one treasure** and no more than **nine treasures** must be present.

### Sample CSV Files

#### Valid CSV Files

Each valid CSV adheres to the validation rules mentioned above.

##### Valid CSV 1

```
0,0,0,0,0,0,1,2
0,0,1,1,0,0,0,0
0,0,0,0,1,0,0,2
0,0,0,0,0,0,1,0
0,1,0,0,0,0,0,0
0,0,0,1,0,0,0,0
0,0,0,0,0,1,0,0
1,0,0,0,0,0,0,1
```

**Explanation:**

- **Total Mines**: 10
- **Main Diagonal Mine**: Only cell `(8,8)` has a mine.
- **Adjacent Mines**: Cells `(2,3)` and `(2,4)` are adjacent horizontally.
- **Treasures**: Two treasures at `(1,8)` and `(3, 8)`.

##### Valid CSV 2

```
1,0,0,0,0,0,0,1
0,0,1,0,0,0,0,0
0,0,0,0,1,0,0,0
0,1,0,0,0,0,0,1
0,0,0,0,0,0,1,0
0,0,0,0,0,0,1,0
0,0,0,1,0,0,0,0
0,0,0,0,0,1,0,2
```

**Explanation:**

- **Total Mines**: 10
- **Main Diagonal Mine**: Only cell `(1,1)` has a mine.
- **Adjacent Mines**: Cells `(5,7)` and `(6,7)` are adjacent vertically.
- **Treasures**: One treasure at `(8,8)`.

##### Valid CSV 3

```
0,0,0,0,0,2,0,1
0,0,0,0,1,0,0,0
0,0,1,0,0,0,0,0
0,0,0,0,0,1,0,1
0,0,0,2,0,0,0,1
0,1,0,0,0,0,0,0
0,2,0,1,0,0,0,0
1,0,0,0,0,0,1,0
```

**Explanation:**

- **Total Mines**: 10
- **Main Diagonal Mine**: Only cell `(3,3)` has a mine.
- **Adjacent Mines**: Cells `(4,8)` and `(5,8)` are adjacent vertically.
- **Treasures**: Two treasures at `(5, 4)` and `(7,2)`.

#### Invalid CSV Files

Each invalid CSV violates at least one of the validation rules.

##### Invalid CSV 1: Incorrect Number of Mines

```
1,0,0,0,0,0,0,0
0,0,1,0,0,0,0,0
0,0,0,1,0,0,0,0
0,0,0,0,1,0,0,0
0,0,0,0,0,1,0,0
0,0,0,0,0,0,1,0
0,0,0,0,0,0,0,1
0,0,0,0,0,0,0,2
```

**Issues:**

- **Total Mines**: 7 (less than required 10).
- **Main Diagonal Mine**: Only cell `(1,1)` has a mine.
- **At Least One Mine per Row and Column**: Row 8 has no mines.

##### Invalid CSV 2: Multiple Mines on Main Diagonal

```
1,0,0,0,0,0,0,1
0,1,0,1,0,0,0,0
0,0,1,0,0,0,0,0
0,0,0,1,0,0,0,0
0,0,0,0,1,0,0,0
0,0,0,0,0,1,0,0
0,0,0,0,0,0,1,0
0,0,0,0,0,0,0,2
```

**Issues:**

- **Total Mines**: 9 (less than required 10).
- **Main Diagonal Mines**: Cells `(1,1)`, `(2,2)`, . . . `(7,7)` each have mines, violating the rule of exactly one mine on the main diagonal.
- **At Least One Mine per Row and Column**: Row 8 has no mines.

##### Invalid CSV 3: No Adjacent Mine Pair

```
1,0,0,0,0,0,1,0
0,0,0,1,0,0,0,0
0,1,0,0,0,0,0,0
1,0,0,0,0,1,0,0
0,0,0,0,0,0,0,0
0,1,0,0,1,0,0,0
0,0,0,1,0,0,0,0
0,0,0,0,0,0,0,2
```

**Issues:**

- **Total Mines**: 9 (less than required 10).
- **Main Diagonal Mine**: Only cell `(1,1)` has a mine.
- **Adjacent Mines**: No two mines are adjacent horizontally or vertically, violating the rule of exactly one pair of adjacent mines.
- **At Least One Mine per Row and Column**: Row 8 has no mines.

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/AkulaPhanidhar/Minesweeper.git
   ```

   ```bash
   cd Minesweeper
   ```

2. **(Optional) Create a Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   ```

   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   The game primarily uses standard Python libraries, so no additional installations are typically required. Ensure Tkinter is installed as per the [Requirements](#requirements) section.

---

## Usage

1. **Run the Game**

   ```bash
   python3 minesweeper.py
   ```

2. **Selecting Game Level**

   Upon starting, you'll be prompted to select a difficulty level:

   ```
   Choose a level:
   1. Beginner (8x8, 10 mines, 2 treasures)
   2. Intermediate (16x16, 40 mines, 4 treasures)
   3. Expert (30x16, 99 mines, 6 treasures)

   Enter the number:
   ```

3. **Testing Mode (Beginner Level Only)**

   After selecting the Beginner level, you'll have the option to enter Testing Mode to load a predefined board from a CSV file.

   ```
   Would you like to enter testing mode? (y/n): y
   Enter the path to the test board CSV file: ./valid_board_1.csv

   Test board is valid with 10 mines and 2 treasures. Starting the game...
   ```

   - **Loading a Valid CSV**

     Ensure your CSV file adheres to the following rules:

     - **Format**: 8 rows with 8 values each, separated by commas.
     - **Values**:
       - `0`: Empty cell.
       - `1`: Mine.
       - `2`: Treasure.
     - **Validation Rules**:
       - Exactly 10 mines (`1`).
       - At least one mine in each row and each column.
       - Only one mine on the main diagonal (where row index equals column index).
       - Exactly one pair of adjacent mines (horizontally or vertically).
       - At least one treasure and no more than 9 treasures.

   - **Example Valid CSV**

     ```
     0,0,0,0,0,0,1,2
     0,0,1,1,0,0,0,0
     0,0,0,0,1,0,0,2
     0,0,0,0,0,0,1,0
     0,1,0,0,0,0,0,0
     0,0,0,1,0,0,0,0
     0,0,0,0,0,1,0,0
     1,0,0,0,0,0,0,1
     ```

   - **Loading an Invalid CSV**

     If the CSV does not meet the validation criteria, the game will inform you of the specific issue and prompt whether to retry or proceed with a random board.

     ```
     Invalid board: Number of mines must be exactly 10. Found 9.
     Would you like to try entering testing mode again? (y/n): n
     ```

4. **Choose the View**

   After setting up the game (either in testing mode or normal mode), you'll be prompted to choose between the GUI and Text views.

   ```
   Choose a view:
   1. GUI
   2. Text

   Enter the number:
   ```

   - **GUI Mode**

     Selecting `1` launches the graphical interface.

     ```
     --------------------
     Opening GUI View...
     --------------------
     ```

     - **Interacting with the GUI**:
       - **Reveal a Cell**: Left-click on a cell to reveal it.
       - **Flag/Unflag a Cell**: Right-click on a cell to flag or unflag it.
       - **Game Over**: If you reveal a mine, you lose. If you find the treasure, you win.
       - **Restart or Exit**: Upon game conclusion, you'll be prompted to play again or exit.

   - **Text Mode**

     Selecting `2` launches the console-based interface.

     ```
     --------------------
     Opening Text View...
     --------------------
     ```

     - **Interacting with the Text View**:
       - **Reveal a Cell**: Enter `r x y`, where `x` and `y` are the row and column numbers (1-based).
       - **Flag/Unflag a Cell**: Enter `f x y`, where `x` and `y` are the row and column numbers (1-based).
       - **Game Over**: Revealing a mine results in a loss, while finding the treasure results in a win.
       - **Restart or Exit**: After the game concludes, you'll be prompted to play again or exit.

---

## Gameplay Mechanics

- **Objective**: Reveal all safe cells without triggering a mine and find the hidden treasure.

- **Cells**:

  - **Empty (`0`)**: Safe cells without mines or treasures.
  - **Mine (`M`)**: Hidden mines; revealing one results in a loss.
  - **Treasure (`T`)**: Hidden treasure; finding it results in an immediate win.
  - **Flag (`F`)**: Mark cells you suspect contain mines.

- **Gameplay Mechanics**:

  - **Revealing Cells**: Revealing a cell without a mine or treasure will display the number of adjacent mines.
  - **Flagging Cells**: Use flags to mark cells you believe contain mines.
  - **Winning the Game**:
    - Reveal all safe cells.
    - Find the hidden treasure.
  - **Losing the Game**:
    - Reveal a mine.

- **Timer**: Keep track of how long you take to complete the game.

---

## Challenges and Solutions

During the development of **Minesweeper with Hidden Treasure**, several challenges were encountered. Below are the key challenges and the solutions implemented to overcome them:

1. **Ensuring Test Board Utilization Across Views**

   - **Challenge**: After loading a valid test board from a CSV file, the GUI and Text views were not consistently using the predefined board, resulting in random boards being generated instead.
   - **Solution**: Updated the `GameModel` to internally store the `test_board` and modified the initialization logic to prioritize loading from `test_board` when available. This ensured that both GUI and Text views consistently used the predefined board in Testing Mode.

2. **Maintaining Line Count and Functionality**

   - **Challenge**: After updates, the line count of the code was significantly reduced, raising concerns about potential loss of functionality.
   - **Solution**: Conducted a thorough review to ensure that all functionalities from the original code were preserved. Confirmed that essential features like MVC architecture, Testing Mode, flagging, timer, and game over mechanisms were intact. Optimized code for better readability and efficiency without sacrificing functionality.

3. **Implementing Design by Contract (DBC)**

   - **Challenge**: Integrating DBC annotations (`Requires:` and `Ensures:`) without cluttering the code or affecting performance.
   - **Solution**: Added DBC annotations as structured docstrings within each method, clearly specifying preconditions and postconditions. This approach maintained code cleanliness while enhancing documentation and reliability.

4. **CSV Validation Complexity**

   - **Challenge**: Implementing comprehensive validation rules for CSV files to ensure game integrity.
   - **Solution**: Developed a robust `load_and_validate_test_board` function that meticulously checks each validation rule, providing specific error messages for different types of validation failures. This facilitated easier debugging and user guidance when loading invalid CSV files.

5. **User Experience in Testing Mode**
   - **Challenge**: Ensuring a seamless user experience when entering and exiting Testing Mode, especially when dealing with invalid CSV files.
   - **Solution**: Implemented clear and informative prompts that guide users through the Testing Mode process. Provided options to retry loading a CSV file or proceed with a random board if validation fails, enhancing user control and flexibility.

---

## Future Work

While the current version of **Minesweeper with Hidden Treasure** is feature-rich and robust, there are several avenues for future enhancements:

1. **Extended Difficulty Levels for Testing Mode**

   - Implement Testing Modes for Intermediate and Expert levels, allowing users to load predefined boards with larger sizes and more complex configurations.

2. **Graphical Enhancements**

   - Enhance the GUI with better graphics, animations, and responsive design to improve user engagement and aesthetics.

3. **Sound Effects**

   - Introduce sound effects for actions like revealing a cell, flagging, winning, or losing to enrich the gaming experience.

4. **High Scores and Leaderboards**

   - Implement a high scores system to track and display the fastest completion times, fostering competition among players.

5. **Save and Load Game State**

   - Allow players to save their current game state and resume later, providing greater flexibility and convenience.

6. **Customization Options**

   - Enable users to customize game settings such as grid size, number of mines, and number of treasures beyond the predefined levels.

7. **Cross-Platform Compatibility**

   - Optimize the game for seamless operation across different operating systems, including mobile platforms.

8. **Automated Testing Suite**
   - Develop an automated testing suite to continuously verify the integrity and functionality of the game, ensuring reliability with each update.

---

## Conclusion

**Minesweeper with Hidden Treasure** successfully blends the timeless appeal of the classic Minesweeper game with innovative features that enhance gameplay and testing capabilities. By adhering to the Model-View-Controller (MVC) design pattern and incorporating Design by Contract (DBC) principles, the project ensures a clean, maintainable, and scalable codebase. The introduction of Testing Mode with CSV board loading provides developers and testers with powerful tools to validate game scenarios and maintain high-quality standards. With its dual interfaces, robust features, and thoughtful design, the game offers an engaging and reliable experience for players of all preferences.

---

## References

- [Python Official Documentation](https://docs.python.org/3/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Model-View-Controller (MVC) Design Pattern](https://en.wikipedia.org/wiki/Model–view–controller)
- [Design by Contract (DBC) Principles](https://en.wikipedia.org/wiki/Design_by_contract)
- [Python CSV Module](https://docs.python.org/3/library/csv.html)
