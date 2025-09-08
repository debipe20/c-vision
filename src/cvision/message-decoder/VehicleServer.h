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
#include <vector>
#include "ServerList.h"
#include "BasicVehicle.h"
#include "Timestamp.h"

using std::cout;
using std::endl; 
using std::vector;
using std::string;
using std::ifstream;

class VehicleServer
{
private:
    vector<ServerList> VehicleServerList;
    ServerList vehicleinfo;
    int timedOutVehicleID{};

public:
    VehicleServer();
    ~VehicleServer();
    void managingVehicleServerList(BasicVehicle basicVehicle);
    void processBSM(BasicVehicle basicVehicle);
    bool checkAddVehicleIDToVehicleServerList(int vehicleID);
    bool checkUpdateVehicleIDInVehicleServerList(int vehicleID);
    bool checkDeleteTimedOutVehicleIDFromList();
    
    void setTimedOutVehicleID(int vehicleID);
    int getTimedOutVehicleID();
    double getCurrentTimeInSeconds();
};

