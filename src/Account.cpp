#include "Account.h"

Account::Account(string username, string type, int creditCents) {
    this->username = username;
    this->type = type;
    this->creditCents = creditCents;
}

string Account::getUsername() {
    return username;
}

string Account::getType() {
    return type;
}

int Account::getCreditCents() {
    return creditCents;
}

void Account::setCreditCents(int amountCents) {
    creditCents = amountCents;
}

bool Account::isAdmin() {
    return type == "AA";
}

bool Account::canBuy() {
    return type != "SS";
}

bool Account::canSell() {
    return type != "BS";
}
