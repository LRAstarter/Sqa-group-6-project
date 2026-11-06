#include <fstream>
#include "FrontEnd.h"

FrontEnd::FrontEnd(string accountsFile, string gamesFile, string collectionFile, string dailyFile) {
    loggedIn = false;
    currentUsername = "";
    accountsFilename = accountsFile;
    gamesFilename = gamesFile;
    collectionFilename = collectionFile;
    dailyFilename = dailyFile;
}

void FrontEnd::run(istream& input, ostream& output) {
    vector<Game> loadedGames;
    if (!fileManager.loadAccounts(accountsFilename, accounts) ||
        !fileManager.loadAvailableGames(gamesFilename, loadedGames) ||
        !fileManager.loadGameCollection(collectionFilename, gameCollection)) {
        displayMessage(output, "Error: could not read the input files");
        return;
    }
    availableGames.setGames(loadedGames);
    ofstream emptyDailyFile(dailyFilename.c_str());
    emptyDailyFile.close();

    string command;
    while (readLine(input, output, "Transaction: ", command)) {
        processCommand(command, input, output);
    }
}

void FrontEnd::processCommand(string command, istream& input, ostream& output) {
    if (command == "login") {
        if (loggedIn) {
            displayMessage(output, "Error: already logged in");
            return;
        }
        string username;
        if (!readLine(input, output, "Username: ", username)) return;
        if (login(username)) displayMessage(output, "Login accepted");
        else displayMessage(output, "Error: login failed");
        return;
    }

    if (!loggedIn) {
        displayMessage(output, "Error: you must log in first");
        return;
    }
    Account* user = findAccount(currentUsername);

    if (command == "logout") {
        if (logout()) displayMessage(output, "Logout accepted");
        else displayMessage(output, "Error: could not write the daily transaction file");
    } else if (command == "create") {
        if (!user->isAdmin()) {
            displayMessage(output, "Error: only an admin can create accounts");
            return;
        }
        string username, type;
        if (!readLine(input, output, "New username: ", username)) return;
        if (username == "" || username.size() > 15 || findAccount(username) != nullptr || deletedUsers.count(username) > 0) {
            displayMessage(output, "Error: that username cannot be used");
            return;
        }
        if (!readLine(input, output, "Account type: ", type)) return;
        if (createAccount(username, type)) displayMessage(output, "Account created");
        else displayMessage(output, "Error: invalid account type");
    } else if (command == "delete") {
        if (!user->isAdmin()) {
            displayMessage(output, "Error: only an admin can delete accounts");
            return;
        }
        string username;
        if (!readLine(input, output, "Username to delete: ", username)) return;
        if (deleteAccount(username)) displayMessage(output, "Account deleted");
        else displayMessage(output, "Error: that account cannot be deleted");
    } else if (command == "sell") {
        if (!user->canSell()) {
            displayMessage(output, "Error: buy-standard accounts cannot sell");
            return;
        }
        string gameName, priceText;
        int priceCents;
        if (!readLine(input, output, "Game name: ", gameName)) return;
        if (!readLine(input, output, "Price: ", priceText)) return;
        if (!parseMoney(priceText, priceCents)) {
            displayMessage(output, "Error: invalid price");
            return;
        }
        if (sell(gameName, priceCents)) displayMessage(output, "Game put up for sale");
        else displayMessage(output, "Error: that game cannot be sold");
    } else if (command == "buy") {
        if (!user->canBuy()) {
            displayMessage(output, "Error: sell-standard accounts cannot buy");
            return;
        }
        string gameName, sellerUsername;
        if (!readLine(input, output, "Game name: ", gameName)) return;
        if (!readLine(input, output, "Seller username: ", sellerUsername)) return;
        if (buy(gameName, sellerUsername)) displayMessage(output, "Purchase accepted");
        else displayMessage(output, "Error: that game cannot be bought");
    } else if (command == "refund") {
        if (!user->isAdmin()) {
            displayMessage(output, "Error: only an admin can refund");
            return;
        }
        string buyerUsername, sellerUsername, amountText;
        int amountCents;
        if (!readLine(input, output, "Buyer username: ", buyerUsername)) return;
        if (!readLine(input, output, "Seller username: ", sellerUsername)) return;
        if (!readLine(input, output, "Refund amount: ", amountText)) return;
        if (!parseMoney(amountText, amountCents)) {
            displayMessage(output, "Error: invalid amount");
            return;
        }
        if (refund(buyerUsername, sellerUsername, amountCents)) displayMessage(output, "Refund accepted");
        else displayMessage(output, "Error: that refund cannot be made");
    } else if (command == "addcredit") {
        string amountText, username = currentUsername;
        int amountCents;
        if (!readLine(input, output, "Amount: ", amountText)) return;
        if (!parseMoney(amountText, amountCents)) {
            displayMessage(output, "Error: invalid amount");
            return;
        }
        if (user->isAdmin()) {
            if (!readLine(input, output, "Username: ", username)) return;
        }
        if (addCredit(username, amountCents)) displayMessage(output, "Credit added");
        else displayMessage(output, "Error: credit cannot be added");
    } else if (command == "list") {
        const vector<Game>& games = availableGames.getGames();
        if (games.size() == 0) {
            displayMessage(output, "There are no games for sale right now");
        }
        for (int i = 0; i < (int)games.size(); i++) {
            int cents = games[i].getPriceCents();
            string zero = "";
            if (cents % 100 < 10) zero = "0";
            output << games[i].getName() << " | " << games[i].getSellerUsername()
                   << " | " << cents / 100 << "." << zero << cents % 100 << endl;
        }
    } else {
        displayMessage(output, "Error: unknown transaction");
    }
}

bool FrontEnd::login(string username) {
    if (findAccount(username) == nullptr) return false;
    loggedIn = true;
    currentUsername = username;
    return true;
}

bool FrontEnd::logout() {
    Account* user = findAccount(currentUsername);
    Transaction transaction;
    transaction.code = "00";
    transaction.username = user->getUsername();
    transaction.userType = user->getType();
    transaction.amountCents = user->getCreditCents();
    recordTransaction(transaction);
    bool written = fileManager.writeDailyTransactions(dailyFilename, sessionTransactions);
    resetSession();
    return written;
}

bool FrontEnd::createAccount(string username, string type) {
    if (type != "AA" && type != "FS" && type != "BS" && type != "SS") return false;
    accounts.push_back(Account(username, type, 0));
    Transaction transaction;
    transaction.code = "01";
    transaction.username = username;
    transaction.userType = type;
    recordTransaction(transaction);
    return true;
}

bool FrontEnd::deleteAccount(string username) {
    Account* account = findAccount(username);
    if (account == nullptr || username == currentUsername) return false;

    Transaction transaction;
    transaction.code = "02";
    transaction.username = username;
    transaction.userType = account->getType();
    transaction.amountCents = account->getCreditCents();
    recordTransaction(transaction);

    for (int i = 0; i < (int)accounts.size(); i++) {
        if (accounts[i].getUsername() == username) {
            accounts.erase(accounts.begin() + i);
            break;
        }
    }
    availableGames.removeSeller(username);
    gameCollection.erase(username);
    deletedUsers.insert(username);
    return true;
}

bool FrontEnd::sell(string gameName, int priceCents) {
    if (gameName == "" || gameName.size() > 25) return false;
    if (priceCents < 0 || priceCents > 99999) return false;
    if (availableGames.containsName(gameName)) return false;

    availableGames.reserveName(gameName);
    Transaction transaction;
    transaction.code = "03";
    transaction.gameName = gameName;
    transaction.sellerUsername = currentUsername;
    transaction.amountCents = priceCents;
    recordTransaction(transaction);
    return true;
}

bool FrontEnd::buy(string gameName, string sellerUsername) {
    const Game* game = availableGames.findGame(gameName, sellerUsername);
    Account* buyer = findAccount(currentUsername);
    Account* seller = findAccount(sellerUsername);
    if (game == nullptr || seller == nullptr) return false;
    if (ownsGame(currentUsername, gameName)) return false;
    if (buyer->getCreditCents() < game->getPriceCents()) return false;

    buyer->setCreditCents(buyer->getCreditCents() - game->getPriceCents());
    seller->setCreditCents(seller->getCreditCents() + game->getPriceCents());
    gameCollection[currentUsername].insert(gameName);
    Transaction transaction;
    transaction.code = "04";
    transaction.gameName = gameName;
    transaction.sellerUsername = sellerUsername;
    transaction.buyerUsername = currentUsername;
    transaction.amountCents = game->getPriceCents();
    recordTransaction(transaction);
    return true;
}

bool FrontEnd::refund(string buyerUsername, string sellerUsername, int amountCents) {
    Account* buyer = findAccount(buyerUsername);
    Account* seller = findAccount(sellerUsername);
    if (buyer == nullptr || seller == nullptr) return false;
    if (amountCents <= 0 || seller->getCreditCents() < amountCents) return false;

    buyer->setCreditCents(buyer->getCreditCents() + amountCents);
    seller->setCreditCents(seller->getCreditCents() - amountCents);
    Transaction transaction;
    transaction.code = "05";
    transaction.buyerUsername = buyerUsername;
    transaction.sellerUsername = sellerUsername;
    transaction.amountCents = amountCents;
    recordTransaction(transaction);
    return true;
}

bool FrontEnd::addCredit(string username, int amountCents) {
    Account* account = findAccount(username);
    if (account == nullptr || amountCents <= 0) return false;
    if (creditAddedThisSession[username] + amountCents > 100000) return false;
    if (account->getCreditCents() + amountCents > 99999900) return false;

    account->setCreditCents(account->getCreditCents() + amountCents);
    creditAddedThisSession[username] += amountCents;
    Transaction transaction;
    transaction.code = "06";
    transaction.username = username;
    transaction.userType = account->getType();
    transaction.amountCents = account->getCreditCents();
    recordTransaction(transaction);
    return true;
}

Account* FrontEnd::findAccount(string username) {
    for (int i = 0; i < (int)accounts.size(); i++) {
        if (accounts[i].getUsername() == username) return &accounts[i];
    }
    return nullptr;
}

bool FrontEnd::ownsGame(string username, string gameName) {
    map<string, set<string> >::iterator owner = gameCollection.find(username);
    return owner != gameCollection.end() && owner->second.count(gameName) > 0;
}

bool FrontEnd::readLine(istream& input, ostream& output, string prompt, string& value) {
    output << prompt;
    if (!getline(input, value)) return false;
    if (value.size() > 0 && value[value.size() - 1] == '\r') {
        value.erase(value.size() - 1);
    }
    return true;
}

bool FrontEnd::parseMoney(string text, int& cents) {
    if (text.size() == 0 || text.size() > 9) return false;
    int start = 0;
    if (text[0] == '-') start = 1;
    int dollars = 0, pennies = 0, digits = 0, decimals = 0;
    bool afterPoint = false;
    for (int i = start; i < (int)text.size(); i++) {
        if (text[i] == '.' && !afterPoint) {
            afterPoint = true;
        } else if (text[i] >= '0' && text[i] <= '9') {
            if (!afterPoint) {
                dollars = dollars * 10 + (text[i] - '0');
            } else if (decimals < 2) {
                pennies = pennies * 10 + (text[i] - '0');
                decimals++;
            } else {
                return false;
            }
            digits++;
        } else {
            return false;
        }
    }
    if (digits == 0) return false;
    if (decimals == 1) pennies = pennies * 10;
    cents = dollars * 100 + pennies;
    if (start == 1) cents = -cents;
    return true;
}

void FrontEnd::displayMessage(ostream& output, string message) {
    output << message << endl;
}

void FrontEnd::recordTransaction(Transaction transaction) {
    sessionTransactions.push_back(transaction);
}

void FrontEnd::resetSession() {
    loggedIn = false;
    currentUsername = "";
    sessionTransactions.clear();
    creditAddedThisSession.clear();
    deletedUsers.clear();
    availableGames.clear();
}
