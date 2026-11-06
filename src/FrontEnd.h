#ifndef FRONTEND_H
#define FRONTEND_H

#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include "Account.h"
#include "AvailableGames.h"
#include "FileManager.h"
#include "Game.h"
#include "Transaction.h"
using namespace std;

class FrontEnd {
private:
    bool loggedIn;
    string currentUsername;
    string accountsFilename;
    string gamesFilename;
    string collectionFilename;
    string dailyFilename;
    vector<Account> accounts;
    AvailableGames availableGames;
    map<string, set<string> > gameCollection;
    vector<Transaction> sessionTransactions;
    map<string, int> creditAddedThisSession;
    set<string> deletedUsers;
    FileManager fileManager;

    void processCommand(string command, istream& input, ostream& output);
    bool login(string username);
    bool logout();
    bool createAccount(string username, string type);
    bool deleteAccount(string username);
    bool sell(string gameName, int priceCents);
    bool buy(string gameName, string sellerUsername);
    bool refund(string buyerUsername, string sellerUsername, int amountCents);
    bool addCredit(string username, int amountCents);
    Account* findAccount(string username);
    bool ownsGame(string username, string gameName);
    bool readLine(istream& input, ostream& output, string prompt, string& value);
    bool parseMoney(string text, int& cents);
    void displayMessage(ostream& output, string message);
    void recordTransaction(Transaction transaction);
    void resetSession();

public:
    FrontEnd(string accountsFile, string gamesFile, string collectionFile, string dailyFile);
    void run(istream& input, ostream& output);
};

#endif
