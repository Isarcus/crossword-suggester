# Crossword Word Suggester
This program suggests words based on patterns of letters you know and don't know!

## How to run the code:
1. Clone this repository with Git:
```
git clone https://github.com/Isarcus/crossword-suggester.git
```
2. Compile the code from the repository's root directory:
```
make release
```
3. Run the program with a dictionary file of your choice. The words in these files must be separated by newlines (CRLF and LF are both OK). Some example dictionaries are provide in the `data` folder. Here is an example of how to run the program:
```
./suggester data/american.txt
```
4. Enter *patterns* to query the dictionary. I haven't included anything fancy (yet) like regular expressions, just simple patterns of *letters* and *blanks*. Blanks are represented with asterisks. For example, the pattern:
```
FR**T
```
will return all words whose first letter is F, second letter is R, and fifth letter is T, and whose total length is five letters. The third and fourth letters could be anything. Special characters and punctuation are not supported (yet).
