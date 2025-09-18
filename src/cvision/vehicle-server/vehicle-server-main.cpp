/*
**********************************************************************************
vehicle-server-main.cpp
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------

**********************************************************************************
*/

#include "VehicleServer.h"
#include <UdpSocket.h>

using std::getenv;

int main()
{
    const char *home = getenv("HOME");
    if (!home)
        return 1;

    const string config_file_path = string(home) + "/Desktop/debashis-workspace/config/anl-master-config.json";

    Json::Value jsonObject;
    // std::ifstream configJson("/home/debashis/Desktop/debashis-workspace/config/anl-master-config.json");
    std::ifstream configJson(config_file_path);
    string configJsonString((std::istreambuf_iterator<char>(configJson)), std::istreambuf_iterator<char>());
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    string errors{};
    reader->parse(configJsonString.c_str(), configJsonString.c_str() + configJsonString.size(), &jsonObject, &errors);
    delete reader;

    VehicleServer vehicleServer;
    BasicVehicle basicVehicle;
    const string HostIP = jsonObject["IPAddress"]["HostIp"].asString();
    UdpSocket vehicleServerSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["VehicleServer"].asInt()));
    // const int v2xDataManagerPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["V2XDataManager"].asInt());
    // const int mapReceiverPortNo = static_cast<short unsigned int>(jsonObject["PortNumber"]["VehicleServer"].asInt());
    char receiveBuffer[2048];
    int msgType{};
    string sendingJsonString{};
    double currentTime{};

    while (true)
    {
        vehicleServerSocket.receiveData(receiveBuffer, sizeof(receiveBuffer));
        string receivedJsonString(receiveBuffer);
        currentTime = static_cast<double>(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()));
        
        msgType = vehicleServer.getMessageType(receivedJsonString);

        if (msgType == MsgEnum::DSRCmsgID_bsm)
        {
            cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Received BSM" << endl;
            basicVehicle.json2BasicVehicle(receivedJsonString);
            vehicleServer.processBSM(basicVehicle);
            // vehicleServerSocket.sendData(HostIP, static_cast<short unsigned int>(v2xDataManagerPort), sendingJsonString);
        }

    //     if (msgType == MsgEnum::DSRCmsgID_map)
    //     {
    //         cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Received MAP" << endl;

    //         sendingJsonString = msgDecoder.mapDecoder(receivedPayload);
    //         vehicleServerSocket.sendData(HostIP, static_cast<short unsigned int>(mapReceiverPortNo), sendingJsonString);
    //         cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Decoded MAP" << endl;
    //     }

    

    //     else if (msgType == MsgEnum::DSRCmsgID_spat)
    //     {
    //         cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Received SPaT" << endl;
    //         sendingJsonString = msgDecoder.spatDecoder(receivedPayload);
    //         vehicleServerSocket.sendData(HostIP, static_cast<short unsigned int>(v2xDataManagerPort), sendingJsonString);
    //     }
    }

    return 0;
}