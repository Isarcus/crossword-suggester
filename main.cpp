#include "Suggester.h"

#include <vector>
#include <string>
#include <iostream>
#include <fstream>

std::vector<std::string> loadDict(std::string filepath);

bool enforceLength = true;

int main(int argc, char** argv)
{
    if (argc != 2)
    {
        std::cout << "Usage: \033[1;30m./suggester dictionary.txt\033[0m\n";
        exit(0);
    }

    Suggester sug(loadDict(argv[1]));
    std::string input;
    while (true)
    {
        std::cout << "Please enter a pattern, or Q to quit:\n -> \033[1;32m";
        std::getline(std::cin, input);
        std::cout << "\033[0m";

        if (input.empty())
        {
            continue;
        }
        else if (input.size() == 1 && std::toupper(input[0]) == 'Q')
        {
            break;
        }
        else
        {
            std::vector<const char*> result = sug.matchPattern(input, enforceLength);
            for (auto word : result)
            {
                std::cout << " -> " << word << '\n';
            }
        }
    }
}

std::vector<std::string> loadDict(std::string filepath)
{
    std::ifstream is(filepath);
    if (!is)
    {
        std::cerr << "Error: Couldn't open input file at " << filepath << std::endl;
        exit(1);
    }

    std::vector<std::string> list;
    std::string word;
    while (getline(is, word))
    {
        // Handles CRLF line endings
        if (word.back() == '\r')
        {
            list.push_back(word.substr(0, word.size() - 1));
        }
        else
        {
            list.push_back(word);
        }
    }

    return list;
}
