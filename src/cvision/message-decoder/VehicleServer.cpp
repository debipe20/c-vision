/*
**********************************************************************************
VehicleServer.cpp
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------

**********************************************************************************
*/
#include "VehicleServer.h"
#include <algorithm>

const double TIME_GAP_BETWEEN_RECEIVING_BSM = 10;

VehicleServer::VehicleServer()
{
}

/*
    - The following method will check whether the received vehicle information is required to add or update  in the VehicleServer List
    - If the received BSM is from a new vehicle, the method will create a vehicle inforamtion object for the vehicle.
    - If vehicle id of the received BSM is already present in the VehicleServer List, the method will update the vehicle position and time.
*/
void VehicleServer::managingVehicleServerList(BasicVehicle basicVehicle)
{
    int vehicleID = basicVehicle.getTemporaryID();
    vehicleinfo.reset();

    if (checkAddVehicleIDToVehicleServerList(vehicleID))
    {
        vehicleinfo.vehicleID = vehicleID;
        vehicleinfo.vehicleType = basicVehicle.getType();
        vehicleinfo.updateTime = getCurrentTimeInSeconds();
        vehicleinfo.vehicleLatitude = basicVehicle.getLatitude_DecimalDegree();
        vehicleinfo.vehicleLongitude = basicVehicle.getLongitude_DecimalDegree();
        vehicleinfo.vehicleElevation = basicVehicle.getElevation_Meter();
        VehicleServerList.push_back(vehicleinfo);
    }

    else if (checkUpdateVehicleIDInVehicleServerList(vehicleID))
    {
        vector<ServerList>::iterator findVehicleIDInList = std::find_if(std::begin(VehicleServerList), std::end(VehicleServerList),
                                                                        [&](ServerList const &p)
                                                                        { return p.vehicleID == vehicleID; });

        findVehicleIDInList->updateTime = getCurrentTimeInSeconds();
        findVehicleIDInList->vehicleLatitude = basicVehicle.getLatitude_DecimalDegree();
        findVehicleIDInList->vehicleLongitude = basicVehicle.getLongitude_DecimalDegree();
        findVehicleIDInList->vehicleElevation = basicVehicle.getElevation_Meter();
    }

}

void VehicleServer::processBSM(BasicVehicle basicVehicle)
{
    int vehicleID{};

    vehicleID = basicVehicle.getTemporaryID();

    vector<ServerList>::iterator findVehicleIDInList = std::find_if(std::begin(VehicleServerList), std::end(VehicleServerList),
                                                                        [&](ServerList const &p)
                                                                        { return p.vehicleID == vehicleID; });

}


/*
    - The following boolean method will determine whether the received vehicle information is required to add in the VehicleServer List
    - If vehicle ID is not present in the VehicleServer list the method will return true. 
*/
bool VehicleServer::checkAddVehicleIDToVehicleServerList(int vehicleID)
{
    bool addVehicleID{false};

    vector<ServerList>::iterator findVehicleIDInList = std::find_if(std::begin(VehicleServerList), std::end(VehicleServerList),
                                                                    [&](ServerList const &p)
                                                                    { return p.vehicleID == vehicleID; });

    if (VehicleServerList.empty())
        addVehicleID = true;

    else if (!VehicleServerList.empty() && findVehicleIDInList == VehicleServerList.end())
        addVehicleID = true;

    return addVehicleID;
}

/*
    - The following boolean method will determine whether the received vehicle information is required to update in the VehicleServer List
    - If vehicle ID is present in the VehicleServer list the method will return true.
*/
bool VehicleServer::checkUpdateVehicleIDInVehicleServerList(int vehicleID)
{
    bool updateVehicleID{false};

    vector<ServerList>::iterator findVehicleIDInList = std::find_if(std::begin(VehicleServerList), std::end(VehicleServerList),
                                                                    [&](ServerList const &p)
                                                                    { return p.vehicleID == vehicleID; });

    if (VehicleServerList.empty())
        updateVehicleID = false;

    else if (!VehicleServerList.empty() && findVehicleIDInList != VehicleServerList.end())
        updateVehicleID = true;

    else if (!VehicleServerList.empty() && findVehicleIDInList == VehicleServerList.end())
        updateVehicleID = false;

    return updateVehicleID;
}

/*
    - The following boolean method will determine whether vehicle information is required to delete from the VehicleServer List
    - If there BSM is not received from a vehicle for more than predifined time(10sec),the method will return true.
    - The method will set the timed out vehicle ID
*/
bool VehicleServer::checkDeleteTimedOutVehicleIDFromList()
{
    bool deleteVehicleInfo{false};

    if (!VehicleServerList.empty())
    {
        for (size_t i = 0; i < VehicleServerList.size(); i++)
        {
            if (getCurrentTimeInSeconds() - VehicleServerList[i].updateTime > TIME_GAP_BETWEEN_RECEIVING_BSM)
            {
                deleteVehicleInfo = true;
                setTimedOutVehicleID(VehicleServerList[i].vehicleID);
                break;
            }
        }
    }

    return deleteVehicleInfo;
}


/*
    - Setter for timed out vehicle
*/
void VehicleServer::setTimedOutVehicleID(int vehicleID)
{
    timedOutVehicleID = vehicleID;
}

/*
    - Getter for timed out vehicle
*/
int VehicleServer::getTimedOutVehicleID()
{
    return timedOutVehicleID;
}

/*
    - Method to obtain current time
*/
double VehicleServer::getCurrentTimeInSeconds()
{
    double currentTime = getPosixTimestamp();

    return currentTime;
}

VehicleServer::~VehicleServer()
{
}


