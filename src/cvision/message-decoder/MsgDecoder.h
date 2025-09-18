/*
**********************************************************************************
MsgDecoder.h
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------

**********************************************************************************
*/

#pragma once
#include <iostream>
#include <iomanip>
#include <vector>
#include <chrono>
#include <fstream>
#include "json/json.h"

using std::cout;
using std::endl;
using std::string;
using std::vector;
using std::ifstream;
using std::ofstream;
using std::fixed;
using std::showpoint;
using std::setprecision;

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
