#ifndef TRANSACTION_H
#define TRANSACTION_H

#include <string>
using namespace std;

struct Transaction {
    string code;
    string username;
    string userType;
    string gameName;
    string sellerUsername;
    string buyerUsername;
    int amountCents = 0;
};

#endif
