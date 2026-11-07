#include <iostream>
#include "FrontEnd.h"
using namespace std;

int main(int argc, char* argv[]) {
    if (argc != 5) {
        cout << "Usage: frontend users.txt games.txt collection.txt daily.txt" << endl;
        return 1;
    }
    FrontEnd frontEnd(argv[1], argv[2], argv[3], argv[4]);
    frontEnd.run(cin, cout);
    return 0;
}
