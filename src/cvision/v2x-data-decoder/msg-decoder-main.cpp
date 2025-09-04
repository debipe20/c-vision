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

    const string config_file_path = string(home) + "/Desktop/debashis-workspace/config/anl-master-config.json";


    Json::Value jsonObject;
    // std::ifstream configJson("/home/debashis/Desktop/debashis-workspace/config/anl-master-config.json");
    std::ifstream configJson(config_file_path);
    string configJsonString((std::istreambuf_iterator<char>(configJson)), std::istreambuf_iterator<char>());
    Json::CharReaderBuilder builder;
    Json::CharReader * reader = builder.newCharReader();
    string errors{};
    reader->parse(configJsonString.c_str(), configJsonString.c_str() + configJsonString.size(), &jsonObject, &errors);        
    delete reader;

    MsgDecoder msgDecoder;
    const string HostIP = jsonObject["IPAddress"]["HostIp"].asString();
    UdpSocket msgDecoderSocket(static_cast<short unsigned int>(jsonObject["PortNumber"]["V2XDataReceiver"].asInt()));
    const int spatManagerPort = static_cast<short unsigned int>(jsonObject["PortNumber"]["V2XDataManager"].asInt());
    
    char receiveBuffer[2048];
    // string receivedPayload{};
    // string extractedPayload{};
    int msgType{};
    string sendingJsonString{};

    while (true)
    {
        msgDecoderSocket.receiveData(receiveBuffer, sizeof(receiveBuffer));
        string receivedPayload(receiveBuffer);
        cout << receivedPayload << endl;
        size_t pos = receivedPayload.find("001");
        cout << pos << endl;
        receivedPayload = receivedPayload.erase(0,pos);
        
        msgType = msgDecoder.getMessageType(receivedPayload);

            if (msgType == MsgEnum::DSRCmsgID_map)
            {
                cout << "Received MAP" <<endl;
            }

            else if (msgType == MsgEnum::DSRCmsgID_bsm)
            {
                cout << "Received BSM" <<endl;
            }

            else if (msgType == MsgEnum::DSRCmsgID_spat)
            {
                cout << "Received SPaT" <<endl;
                sendingJsonString = msgDecoder.spatDecoder(receivedPayload);
                msgDecoderSocket.sendData(HostIP, static_cast<short unsigned int>(spatManagerPort), sendingJsonString);
            }

        // receivedPayload = msgDecoderSocket.receivePayloadHexString();
        // cout << receivedPayload << endl;
        // size_t pos = receivedPayload.find("001");

        // if (pos != string::npos)
        // {
        //     extractedPayload = receivedPayload.erase(0, pos);
        //     msgType = msgDecoder.getMessageType(extractedPayload);

        //     if (msgType == MsgEnum::DSRCmsgID_map)
        //     {

        //     }

        //     else if (msgType == MsgEnum::DSRCmsgID_bsm)
        //     {

        //     }

        //     else if (msgType == MsgEnum::DSRCmsgID_spat)
        //     {

        //     }
        // }
    }
    
    return 0;
}