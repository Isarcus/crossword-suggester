CXX = g++
CXXFLAGS = -g -std=c++17 -Wall -Wextra -Werror -pedantic
SRC = $(wildcard *.cpp)
OUTPUT = suggester

debug: $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(OUTPUT)

release: $(SRC)
	$(CXX) $(CXXFLAGS) -O3 $(SRC) -o $(OUTPUT)

default: debug
