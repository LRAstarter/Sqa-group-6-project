#ifndef FILEMANAGER_H
#define FILEMANAGER_H

#include <map>
#include <set>
#include <string>
#include <vector>
#include "Account.h"
#include "Game.h"
#include "Transaction.h"
using namespace std;

class FileManager {
private:
    string formatTransaction(Transaction transaction);
    string padText(string value, int width);
    string formatMoney(int cents, int width);

public:
    bool loadAccounts(string filename, vector<Account>& accounts);
    bool loadAvailableGames(string filename, vector<Game>& games);
    bool loadGameCollection(string filename, map<string, set<string> >& collection);
    bool writeDailyTransactions(string filename, vector<Transaction> transactions);
};

#endif
