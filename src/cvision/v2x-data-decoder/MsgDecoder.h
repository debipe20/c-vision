#pragma once
#include <iostream>
#include <iomanip>
#include <vector>
// #include <string>
#include <fstream>
#include "json/json.h"

using std::cout;
using std::endl;
using std::string;
using std::vector;
using std::ifstream;

class MsgDecoder
{
private:
    string sendingJsonString;
    string mapIdentifier = "0012";
    string bsmIdentifier = "0014";
    string spatIdentifier = "0013";


public:
    MsgDecoder();
    ~MsgDecoder();

    int getMessageType(string payload);
    string mapDecoder(string mapPayload);
    string spatDecoder(string spatPayload);
    string bsmDecoder(string bsmPayload);
};
