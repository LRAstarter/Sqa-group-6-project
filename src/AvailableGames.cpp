#include "AvailableGames.h"

void AvailableGames::setGames(const vector<Game>& games) {
    this->games = games;
}

const Game* AvailableGames::findGame(string name, string seller) {
    for (int i = 0; i < (int)games.size(); i++) {
        if (games[i].getName() == name && games[i].getSellerUsername() == seller) {
            return &games[i];
        }
    }
    return nullptr;
}

bool AvailableGames::containsName(string name) {
    if (pendingGameNames.count(name) > 0) return true;
    for (int i = 0; i < (int)games.size(); i++) {
        if (games[i].getName() == name) return true;
    }
    return false;
}

void AvailableGames::reserveName(string name) {
    pendingGameNames.insert(name);
}

void AvailableGames::removeSeller(string seller) {
    for (int i = (int)games.size() - 1; i >= 0; i--) {
        if (games[i].getSellerUsername() == seller) {
            games.erase(games.begin() + i);
        }
    }
}

void AvailableGames::clear() {
    pendingGameNames.clear();
}

const vector<Game>& AvailableGames::getGames() {
    return games;
}
