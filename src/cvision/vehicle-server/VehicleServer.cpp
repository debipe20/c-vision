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

const double TIME_GAP_BETWEEN_RECEIVING_BSM = 10;
const double DSRC_RANGE = 800.0;

VehicleServer::VehicleServer()
{
}

int VehicleServer::getMessageType(string jsonString)
{
    int messageType{};
    double timeStamp = getPosixTimestamp();
    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    std::string errors{};
    bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);
    delete reader;

    if (parsingSuccessful)
    {
        if ((jsonObject["MsgType"]).asString() == "MAP")
            messageType = MsgEnum::DSRCmsgID_map;

        else if ((jsonObject["MsgType"]).asString() == "BSM")
            messageType = MsgEnum::DSRCmsgID_bsm;

        else if ((jsonObject["MsgType"]).asString() == "SSM")
            messageType = MsgEnum::DSRCmsgID_ssm;

        else
            cout << "[" << fixed << showpoint << setprecision(4) << timeStamp << "] Message type is unknown" << std::endl;
    }

    return messageType;
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

string VehicleServer::processBSM(string jsonString, BasicVehicle basicVehicle)
{
    int vehicleID{};
    int laneID{};
    int approachID{};
    int signalGroup{};
    string signalStatus{};
    string updatedJsonString{};

    vehicleID = basicVehicle.getTemporaryID();
    managingVehicleServerList(basicVehicle);

    vector<ServerList>::iterator findVehicleIDInList = std::find_if(std::begin(VehicleServerList), std::end(VehicleServerList),
                                                                    [&](ServerList const &p)
                                                                    { return p.vehicleID == vehicleID; });

    findVehicleIDInList->vehicleStatusManager.getVehicleInformationFromMAP(findVehicleIDInList->mapManager, basicVehicle);
    findVehicleIDInList->mapManager.updateMapAge();
    findVehicleIDInList->mapManager.deleteMap();
    findVehicleIDInList->vehicleStatusManager.manageMapStatusInAvailableMapList(findVehicleIDInList->mapManager);
    
    laneID = findVehicleIDInList->vehicleStatusManager.getLaneID();
    approachID = findVehicleIDInList->vehicleStatusManager.getApproachID();
    signalGroup = findVehicleIDInList->vehicleStatusManager.getSignalGroup();
    
    findVehicleIDInList->vehicleLaneID = laneID;
    findVehicleIDInList->vehicleApproachID = approachID;
    findVehicleIDInList->vehicleSignalGroup = signalGroup;
    findVehicleIDInList->vehicleSignalStatus = signalStatus;
    updatedJsonString = updateBsmJsonString(jsonString, laneID, approachID, signalGroup);

    return updatedJsonString;
}

/*
    - The following is responsible for processing the received MAP message
    - The method uses MapManager class to maintain available map list
*/
void VehicleServer::processMap(string jsonString, MapManager mapManager)
{
    double mapReferenceLatitude{};
    double mapReferenceLongitude{};

    mapManager.json2MapPayload(jsonString);
    mapManager.writeMAPPayloadInFile();
    mapManager.getReferencePoint();
    mapReferenceLatitude = mapManager.getMapReferenceLatitude();
    mapReferenceLongitude = mapManager.getMapReferenceLongitude();

    for (size_t i = 0; i < VehicleServerList.size(); i++)
    {
        if (haversineDistance(mapReferenceLatitude, mapReferenceLongitude, VehicleServerList[i].vehicleLatitude, VehicleServerList[i].vehicleLongitude) <= DSRC_RANGE)
        {
            VehicleServerList[i].mapManager.json2MapPayload(jsonString);
            VehicleServerList[i].mapManager.maintainAvailableMapList();
        }
    }
}

/*
    - Method for deleting the timed out vehicle information.
    - The method will find the vehicle information object in Vehicle Server list for timed out vehicle ID and delete that object.
*/
void VehicleServer::deleteTimedOutVehicleInformationFromVehicleServerList()
{
    int veheicleID{};
    if (checkDeleteTimedOutVehicleIDFromList())
    {
        veheicleID = getTimedOutVehicleID();
        vector<ServerList>::iterator findVehicleIDInList = std::find_if(std::begin(VehicleServerList), std::end(VehicleServerList),
                                                                        [&](ServerList const &p)
                                                                        { return p.vehicleID == veheicleID; });

        if (findVehicleIDInList != VehicleServerList.end())
            VehicleServerList.erase(findVehicleIDInList);
    }
}

/*
    - Method for computing haversine distance between two gps coordinates
*/
double VehicleServer::haversineDistance(double lat1, double lon1, double lat2, double lon2)
{
    double lattitudeDifference{};
    double longitudeDifference{};
    double rad{6371};
    double distance{};
    double intermediateCalculation{};

    lattitudeDifference = (lat2 - lat1) * M_PI / 180.0;
    longitudeDifference = (lon2 - lon1) * M_PI / 180.0;

    // convert to radians
    lat1 = (lat1)*M_PI / 180.0;
    lat2 = (lat2)*M_PI / 180.0;

    // apply formula
    intermediateCalculation = pow(sin(lattitudeDifference / 2), 2) + pow(sin(longitudeDifference / 2), 2) * cos(lat1) * cos(lat2);

    distance = 2 * rad * asin(sqrt(intermediateCalculation)) * 1000.0;

    return distance;
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
    - If there BSM is not received from a vehicle for more than predefined time(10sec),the method will return true.
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

/*
    - Method for printing the Vehicle server list
*/
void VehicleServer::printVehicleServerList()
{
    double timeStamp = getPosixTimestamp();
    
    if (!VehicleServerList.empty())
    {
        cout << "Vehicle ID" << " " << "Lane ID" << " " << "Signal Group" << " " << "Update Time" << endl;

        for (size_t i = 0; i < VehicleServerList.size(); i++)
            cout << VehicleServerList[i].vehicleID << " " << VehicleServerList[i].vehicleLaneID << " " << VehicleServerList[i].vehicleSignalGroup << " " << VehicleServerList[i].updateTime << endl;
    }
    
    else
        cout << "[" << fixed << showpoint << setprecision(2) << timeStamp << "] Vehicle Server Lists is empty" << endl;
}



string VehicleServer::updateBsmJsonString(const string& inJson, int laneID, int approachID, int signalGroup, string signalStatus) 
{
    string updatedJsonString{};
    Json::CharReaderBuilder rbuilder;
    rbuilder["collectComments"] = false;

    Json::Value jsonObject;
    string errs{};
    std::istringstream iss(inJson);

    if (!Json::parseFromStream(rbuilder, iss, &jsonObject, &errs)) 
    {
        throw std::runtime_error("JSON parse error: " + errs);
    }

    // create path if missing, then set fields
    jsonObject["BasicVehicle"]["laneID"] = laneID;
    jsonObject["BasicVehicle"]["approachID"] = approachID;
    jsonObject["BasicVehicle"]["signalGroup"] = signalGroup;
    jsonObject["BasicVehicle"]["signalStatus"] = signalStatus;

    Json::StreamWriterBuilder wbuilder;
    wbuilder["commentStyle"] = "None";
    wbuilder["indentation"] = "";                  
    
    updatedJsonString = Json::writeString(wbuilder, jsonObject);

    cout << "Updated BSM Json String is: \n" << updatedJsonString << endl;

    return updatedJsonString;
}


VehicleServer::~VehicleServer()
{
}
