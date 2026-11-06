#ifndef ACCOUNT_H
#define ACCOUNT_H

#include <string>
using namespace std;

class Account {
private:
    string username;
    string type;
    int creditCents;

public:
    Account(string username, string type, int creditCents);
    string getUsername();
    string getType();
    int getCreditCents();
    void setCreditCents(int amountCents);
    bool isAdmin();
    bool canBuy();
    bool canSell();
};

#endif
