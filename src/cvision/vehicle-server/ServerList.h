#pragma once
#include "VehicleServer.h"
#include "VehicleStatusManager.h"
#include "MapManager.h" 


using std::string;

struct ServerList
{
    int vehicleID{};
    string vehicleType{};
    double updateTime{};
    double vehicleLatitude{};
    double vehicleLongitude{};
    double vehicleElevation{};
    int vehicleLaneID{};
    int vehicleApproachID{};
    int vehicleSignalGroup{};
    string vehicleSignalStatus{};
    VehicleStatusManager vehicleStatusManager;
    MapManager mapManager;

    void reset()
    {
        vehicleID = 0;
        vehicleType = "";
        updateTime = 0.0;
        vehicleLatitude = 0.0;
        vehicleLongitude = 0.0;
        vehicleElevation = 0.0;
        vehicleLaneID = 0;
        vehicleApproachID = 0;
        vehicleSignalGroup = 0;
        vehicleSignalStatus = "";
    }
};