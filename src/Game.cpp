#include "Game.h"

Game::Game(string name, string sellerUsername, int priceCents) {
    this->name = name;
    this->sellerUsername = sellerUsername;
    this->priceCents = priceCents;
}

string Game::getName() const {
    return name;
}

string Game::getSellerUsername() const {
    return sellerUsername;
}

int Game::getPriceCents() const {
    return priceCents;
}
