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
#include <sstream>
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
    string processBSM(string jsonString, BasicVehicle basicVehicle);
    void processMap(string jsonString, MapManager mapManager);
    void deleteTimedOutVehicleInformationFromVehicleServerList();
    bool checkAddVehicleIDToVehicleServerList(int vehicleID);
    bool checkUpdateVehicleIDInVehicleServerList(int vehicleID);
    bool checkDeleteTimedOutVehicleIDFromList();
    double haversineDistance(double lat1, double lon1, double lat2, double lon2);
    void setTimedOutVehicleID(int vehicleID);
    int getTimedOutVehicleID();
    double getCurrentTimeInSeconds();
    void printVehicleServerList();
    string updateBsmJsonString(const string& inJson, int laneID, int approachID, int signalGroup, string signalStatus);
};

