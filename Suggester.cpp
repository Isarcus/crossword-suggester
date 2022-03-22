#include "Suggester.h"

#include <algorithm>
#include <cstring>
#include <iostream>
#include <stdexcept>

class WordError : public std::runtime_error
{
public:
    WordError(std::string err) : std::runtime_error(err)
    {}
};

static void makeUpper(std::string& word, char allow = '\0')
{
    for (size_t i = 0; i < word.size(); i++)
    {
        char letter = word[i];
        if (islower(letter))
        {
            word[i] = toupper(letter);
        }
        else if (!isupper(letter) && letter != allow)
        {
            throw WordError("Invalid character in '" + word + "' -- ignoring this word!");
        }
    }
}

Suggester::Suggester(std::vector<std::string> list)
{
    for (std::string word : list)
    {
        try
        {
            makeUpper(word);
        }
        catch(const WordError& e)
        {
            std::cerr << e.what() << '\n';
            continue;
        }

        // Check for duplicates
        if (wordSet.count(word))
            continue;
        else
            wordSet.insert(word);

        // Check word size
        size_t len = word.size();
        if (len > MAX_WORD_LEN)
        {
            std::cerr << "Word is too long, will be ignored: " << word << '\n';
            continue;
        }

        // Add word to 'wordVec'
        size_t idx = wordVec.size();
        wordVec.resize(idx + 1);
        wordVec.back().len = len;
        strcpy(wordVec.back().text, word.c_str());

        // Index word in all relevant sets
        for (size_t i = 0; i < len; i++)
        {
            char letter = word[i];
            auto& lvec = indices[letter - 'A'];
            if (lvec.size() < i + 1)
            {
                lvec.resize(i + 1);
            }
            lvec[i].insert(idx);
        }
    }

    std::cout << "Initialized word suggester with " << wordVec.size() << " words!\n";
}

std::vector<const char*> Suggester::matchPattern(std::string pattern, bool enforceLength) const
{
    try
    {
        makeUpper(pattern, '*');
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
        return {};
    }
    
    int len = pattern.size();

    // If just a string of asterisks, use matchLength() instead
    size_t idx_letter = pattern.find_first_not_of('*');
    if (idx_letter == pattern.npos)
    {
        return matchLength(len, (enforceLength) ? len : -1);
    }

    // Initialize search set
    char letter = pattern[idx_letter];
    std::set<uint32_t> set;
    std::vector<uint32_t> intersection;
    if (idx_letter < indices[letter - 'A'].size())
    {
        for (uint32_t idx : indices[letter - 'A'][idx_letter])
        {
            if (wordVec[idx].len == len || (!enforceLength && wordVec[idx].len > len))
            {
                set.insert(idx);
            }
        }
    }
    idx_letter = pattern.find_first_not_of('*', idx_letter + 1);

    // Main search loop
    while (idx_letter != pattern.npos && set.size())
    {
        letter = pattern[idx_letter];
        if (idx_letter < indices[letter - 'A'].size())
        {
            // Compute set intersection
            const std::set<uint32_t>* reqSet = &indices[letter - 'A'][idx_letter];
            intersection.clear();
            std::set_intersection(set.begin(), set.end(),
                                  reqSet->begin(), reqSet->end(),
                                  std::back_inserter(intersection));
            set = std::set<uint32_t>(intersection.begin(), intersection.end());

            // Update the next letter for the next iteration
            idx_letter = pattern.find_first_not_of('*', idx_letter + 1);
        }
        else
        {
            set.clear();
        }
    }
    
    // Create result vector
    std::vector<const char*> result;
    for (uint32_t idx : set)
    {
        result.push_back(wordVec[idx].text);
    }
    return result;
}

std::vector<const char*> Suggester::matchLength(int minLen, int maxLen) const
{
    std::vector<const char*> result;

    for (const Word& word : wordVec)
    {
        if (word.len >= minLen && word.len <= maxLen)
        {
            result.push_back(word.text);
        }
    }

    return result;
}
