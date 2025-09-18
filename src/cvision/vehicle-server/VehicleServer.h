/*
**********************************************************************************
VehicleServer.h
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
#include <algorithm>
#include "ServerList.h"
#include "BasicVehicle.h"
#include "json/json.h"
#include "Timestamp.h"
#include "AsnJ2735Lib.h"
#include "dsrcConsts.h"
#include "locAware.h"
#include "msgEnum.h"

using std::cout;
using std::endl; 
using std::vector;
using std::string;
using std::ifstream;
using std::fixed;
using std::showpoint;
using std::setprecision;

class VehicleServer
{
private:
    vector<ServerList> VehicleServerList;
    ServerList vehicleinfo;
    int timedOutVehicleID{};

public:
    VehicleServer();
    ~VehicleServer();
    int getMessageType(string jsonString);
    void managingVehicleServerList(BasicVehicle basicVehicle);
    void processBSM(BasicVehicle basicVehicle);
    bool checkAddVehicleIDToVehicleServerList(int vehicleID);
    bool checkUpdateVehicleIDInVehicleServerList(int vehicleID);
    bool checkDeleteTimedOutVehicleIDFromList();
    
    void setTimedOutVehicleID(int vehicleID);
    int getTimedOutVehicleID();
    double getCurrentTimeInSeconds();
};

