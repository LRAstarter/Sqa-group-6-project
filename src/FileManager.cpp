#include <cstdlib>
#include <fstream>
#include "FileManager.h"

bool FileManager::loadAccounts(string filename, vector<Account>& accounts) {
    ifstream file(filename.c_str());
    if (!file) return false;
    string line;
    while (getline(file, line)) {
        if (line.size() < 28) continue;
        string username = line.substr(0, 15);
        username.erase(username.find_last_not_of(' ') + 1);
        if (username == "END") break;
        string credit = line.substr(19, 9);
        credit.erase(credit.find('.'), 1);
        accounts.push_back(Account(username, line.substr(16, 2), atoi(credit.c_str())));
    }
    return true;
}

bool FileManager::loadAvailableGames(string filename, vector<Game>& games) {
    ifstream file(filename.c_str());
    if (!file) return false;
    string line;
    while (getline(file, line)) {
        if (line.size() < 48) continue;
        string name = line.substr(0, 25);
        name.erase(name.find_last_not_of(' ') + 1);
        if (name == "END") break;
        string seller = line.substr(26, 15);
        seller.erase(seller.find_last_not_of(' ') + 1);
        string price = line.substr(42, 6);
        price.erase(price.find('.'), 1);
        games.push_back(Game(name, seller, atoi(price.c_str())));
    }
    return true;
}

bool FileManager::loadGameCollection(string filename, map<string, set<string> >& collection) {
    ifstream file(filename.c_str());
    if (!file) return false;
    string line;
    while (getline(file, line)) {
        if (line.size() < 41) continue;
        string name = line.substr(0, 25);
        name.erase(name.find_last_not_of(' ') + 1);
        if (name == "END") break;
        string owner = line.substr(26, 15);
        owner.erase(owner.find_last_not_of(' ') + 1);
        collection[owner].insert(name);
    }
    return true;
}

bool FileManager::writeDailyTransactions(string filename, vector<Transaction> transactions) {
    ofstream file(filename.c_str(), ios::app);
    if (!file) return false;
    for (int i = 0; i < (int)transactions.size(); i++) {
        file << formatTransaction(transactions[i]) << endl;
    }
    return true;
}

string FileManager::formatTransaction(Transaction transaction) {
    string code = transaction.code;
    if (code == "03") {
        return code + " " + padText(transaction.gameName, 25) + " " + padText(transaction.sellerUsername, 15) + " " + formatMoney(transaction.amountCents, 6);
    }
    if (code == "04") {
        return code + " " + padText(transaction.gameName, 25) + " " + padText(transaction.sellerUsername, 15) + " " + padText(transaction.buyerUsername, 15) + " " + formatMoney(transaction.amountCents, 6);
    }
    if (code == "05") {
        return code + " " + padText(transaction.buyerUsername, 15) + " " + padText(transaction.sellerUsername, 15) + " " + formatMoney(transaction.amountCents, 9);
    }
    return code + " " + padText(transaction.username, 15) + " " + transaction.userType + " " + formatMoney(transaction.amountCents, 9);
}

string FileManager::padText(string value, int width) {
    value = value.substr(0, width);
    while ((int)value.size() < width) {
        value = value + " ";
    }
    return value;
}

string FileManager::formatMoney(int cents, int width) {
    string pennies = to_string(cents % 100);
    if (pennies.size() < 2) pennies = "0" + pennies;
    string text = to_string(cents / 100) + "." + pennies;
    while ((int)text.size() < width) {
        text = "0" + text;
    }
    return text;
}
