#ifndef SUGGESTER_H
#define SUGGESTER_H

#include <string>
#include <vector>
#include <cstdint>
#include <unordered_set>
#include <set>

class Suggester
{
public:
    Suggester(std::vector<std::string> list);

    // @param pattern a pattern consisting of letters (lowercase & 
    //        uppercase treated equally) and asterisks. Asterisks
    //        will be treated as wildcards.
    // @param enforceLength when this is true, the words that are
    //        returned will all be the exact same length as the
    //        pattern string. When false, they will all be *at least*
    //        as long as the pattern string.
    // @return All words that match the pattern.
    std::vector<const char*> matchPattern(std::string pattern, bool enforceLength) const;

    // @return All words whose length fall in the inclusive range [minLen, maxLen]
    std::vector<const char*> matchLength(int minLen, int maxLen) const;

    static constexpr int MAX_WORD_LEN = 31;
    static constexpr int WORD_ALLOC_SIZE = MAX_WORD_LEN + 1;

private:
    struct Word
    {
        char text[WORD_ALLOC_SIZE];
        int len;
    };

    // For keeping track of duplicates
    std::unordered_set<std::string> wordSet;

    // For indexing all words during a 'match' request
    std::vector<Word> wordVec;

    // indices[LET - 'A'][IDX] refers to the set of indices of Words whose
    // that contain the letter 'LET' at index 'IDX'.
    std::vector<std::set<uint32_t>> indices[26];

};

#endif
