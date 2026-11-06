#ifndef AVAILABLEGAMES_H
#define AVAILABLEGAMES_H

#include <set>
#include <string>
#include <vector>
#include "Game.h"
using namespace std;

class AvailableGames {
private:
    vector<Game> games;
    set<string> pendingGameNames;

public:
    void setGames(const vector<Game>& games);
    const Game* findGame(string name, string seller);
    bool containsName(string name);
    void reserveName(string name);
    void removeSeller(string seller);
    void clear();
    const vector<Game>& getGames();
};

#endif
