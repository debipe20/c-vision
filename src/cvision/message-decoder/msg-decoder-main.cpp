/*
**********************************************************************************
msg-decoder-main.cpp
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------

**********************************************************************************
*/

#include "MsgDecoder.h"
#include <UdpSocket.h>
#include "geoUtils.h"
#include "msgEnum.h"
#include <algorithm>
#include <cstdlib>

using std::getenv;

int main() {
    const char* home = getenv("HOME");
    if (!home) return 1;

    const string config_file_path = string(home) + "/Desktop/c-vision/config/anl-master-config.json";


    Json::Value jsonObject;
    // std::ifstream configJson("/home/debashis/Desktop/c-vision/config/anl-master-config.json");
    std::ifstream configJson(config_file_path);
    string configJsonString((std::istreambuf_iterator<char>(configJson)), std::istreambuf_iterator<char>());
    Json::CharReaderBuilder builder;
    Json::CharReader * reader = builder.newCharReader();
    string errors{};
    reader->parse(configJsonString.c_str(), configJsonString.c_str() + configJsonString.size(), &jsonObject, &errors);        
    delete reader;

    MsgDecoder msgDecoder;
    const string HostIP = jsonObject["IPAddress"]["HostIp"].asString();
    UdpSocket msgDecoderSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["MessageDecoder"].asInt()));
    const int vehicleServerPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["VehicleServer"].asInt());
    const int v2xDataManagerPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["V2XDataManager"].asInt());
    char receiveBuffer[2048];
    int msgType{};
    string sendingJsonString{};
    double currentTime{};

    while (true)
    {
        msgDecoderSocket.receiveData(receiveBuffer, sizeof(receiveBuffer));
        string receivedPayload(receiveBuffer);
        
        size_t pos = receivedPayload.find("001");
        receivedPayload = receivedPayload.erase(0,pos);
        currentTime = static_cast<double>(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()));
        msgType = msgDecoder.getMessageType(receivedPayload);
        // cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "]Received following payload: \n" << receivedPayload << endl;

            if (msgType == MsgEnum::DSRCmsgID_map)
            {
                cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Received MAP" <<endl;
                
                sendingJsonString = msgDecoder.mapDecoder(receivedPayload);
                msgDecoderSocket.sendData(HostIP, static_cast<short unsigned int>(vehicleServerPort), sendingJsonString);
                // cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Decoded MAP" << endl;
            }

            else if (msgType == MsgEnum::DSRCmsgID_bsm)
            {
                cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Received BSM" <<endl;
                sendingJsonString = msgDecoder.bsmDecoder(receivedPayload);
                msgDecoderSocket.sendData(HostIP, static_cast<short unsigned int>(vehicleServerPort), sendingJsonString);
            }

            else if (msgType == MsgEnum::DSRCmsgID_spat)
            {
                cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Received SPaT" <<endl;
                sendingJsonString = msgDecoder.spatDecoder(receivedPayload);
                msgDecoderSocket.sendData(HostIP, static_cast<short unsigned int>(vehicleServerPort), sendingJsonString);
                msgDecoderSocket.sendData(HostIP, static_cast<short unsigned int>(v2xDataManagerPort), sendingJsonString);
            }
    }
    
    return 0;
}