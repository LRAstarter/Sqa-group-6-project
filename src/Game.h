#ifndef GAME_H
#define GAME_H

#include <string>
using namespace std;

class Game {
private:
    string name;
    string sellerUsername;
    int priceCents;

public:
    Game(string name, string sellerUsername, int priceCents);
    string getName() const;
    string getSellerUsername() const;
    int getPriceCents() const;
};

#endif
