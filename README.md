# Crossword Maker / Word Suggester

## How to run the code:
1. Clone this repository with Git:
```
git clone https://github.com/Isarcus/crossword-suggester.git
```
2. Compile the C++ code for the word suggester from the repository's root directory:
```
make
```
3. Follow the steps below for running either the [crossword maker](#running-the-crossword-maker) or the [word suggester](#running-just-the-word-suggester):

## Running the crossword maker
4. Ensure that [Python 3](https://www.python.org/downloads/) is installed, and that you have the `numpy` and `pygame` packages.
5. Run the crossword maker. Depending on your installation settings, you may have to replace `python` in the following command with `python3`.
```
python -m gui
```
6. Controls:
 * Left-click selects a square in the crossword.
 * Right-click toggles between blanks and dark squares.
 * Tab changes typing direction.
 * Use arrow keys to move the currently selected square.
 * CTRL+S prompts you to enter a filepath at which to save your crossword. Press Enter to save. If you want to overwrite an existing file, you must press CTRL+Enter.
 * CTRL+L prompts you to enter a filepath from which to import an existing crossword. Press Enter to load.
 * You can click the button that shows a hand holding a pen to request suggestions from the word suggester. These suggestions will be based on the currently selected word in the crossword, which is highlighted in blue. See [below](#running-just-the-word-suggester) for the specifics of how the word suggester works.

## Running *just* the word suggester
4. Run the program with a dictionary file of your choice. The words in these files must be separated by newlines (CRLF and LF are both OK). Some example dictionaries are provided in the `crossword-suggester/data` folder. Here is an example of how to run the program (from the `crossword-suggester` directory):
```
./suggester data/american.txt
```
5. Enter *patterns* to query the dictionary. I haven't included anything fancy (yet) like regular expressions, just simple patterns of *letters* and *blanks*. Blanks are represented with asterisks. For example, the pattern:
```
FR**T
```
will return all words whose first letter is F, second letter is R, and fifth letter is T, and whose total length is five letters. The third and fourth letters could be anything. Special characters and punctuation are not supported (yet).
