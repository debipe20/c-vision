/*
**********************************************************************************
MsgDecoder.cpp
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------

**********************************************************************************
*/

#include "MsgDecoder.h"
#include "AsnJ2735Lib.h"
#include "dsrcConsts.h"
#include "locAware.h"
#include "BasicVehicle.h"
#include "Timestamp.h"

using namespace GeoUtils;
using namespace MsgEnum;

const double KPH_TO_MPS_CONVERSION = 0.277778;
const int RED = 3;
const int FLASHING_RED = 4;
const int PROTECTED_GREEN = 5;
const int PERMISSIVE_GREEN = 6;
const int PERMISSIVE_YELLOW = 7;
const int PROTECTED_YELLOW = 8;
// const int DONOTWALK = 3;
// const int PEDCLEAR = 8;
// const int WALK = 6;

MsgDecoder::MsgDecoder()
{
}

int MsgDecoder::getMessageType(string payload)
{
    int messageType{};
    string subPayload = payload.substr(0, 4);
    vector<string> messageIdentifier{mapIdentifier, bsmIdentifier, spatIdentifier};

    if (messageIdentifier.at(0).compare(subPayload) == 0)
        messageType = MsgEnum::DSRCmsgID_map;

    else if (messageIdentifier.at(1).compare(subPayload) == 0)
        messageType = MsgEnum::DSRCmsgID_bsm;

    else if (messageIdentifier.at(2).compare(subPayload) == 0)
        messageType = MsgEnum::DSRCmsgID_spat;

    return messageType;
}

string MsgDecoder::mapDecoder(string mapPayload)
{
    ofstream outputfile;
    string fmap{};
    string intersection_Name{};
    string mapName{};
    int intersectionID{};
    bool singleFrame = false;
    string deleteFileName = "Map.map.payload";
    string jsonString{};

    Json::Value jsonObject_config;
    std::ifstream configJson("/nojournal/bin/mmitss-phase3-master-config.json");
    string configJsonString((std::istreambuf_iterator<char>(configJson)), std::istreambuf_iterator<char>());
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    string errors{};
    reader->parse(configJsonString.c_str(), configJsonString.c_str() + configJsonString.size(), &jsonObject_config, &errors);
    delete reader;

    Json::Value jsonObject;
    Json::StreamWriterBuilder writeBuilder;
    writeBuilder["commentStyle"] = "None";
    writeBuilder["indentation"] = "";

    outputfile.open("Map.map.payload");
    outputfile << "payload"
               << " "
               << "Map"
               << " " << mapPayload << std::endl;
    outputfile.close();

    fmap = "Map.map.payload";
    intersection_Name = "Map";

    /// instance class LocAware (Map Engine)
    LocAware *plocAwareLib = new LocAware(fmap, singleFrame);
    intersectionID = plocAwareLib->getIntersectionIdByName(intersection_Name);
    mapName = "Map" + std::to_string(intersectionID);
    jsonObject["MsgType"] = "MAP";
    jsonObject["IntersectionName"] = mapName;
    jsonObject["MapPayload"] = mapPayload;
    jsonObject["IntersectionID"] = intersectionID;
    jsonString = Json::writeString(writeBuilder, jsonObject);

    remove(deleteFileName.c_str());
    delete plocAwareLib;

    // double currentTime = static_cast<double>(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()));
    // cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Decoded MAP Json is following: \n" << jsonString << endl;

    return jsonString;
}

string MsgDecoder::spatDecoder(string spatPayload)
{
    string jsonString{};

    /// buffer to hold message payload
    size_t bufSize = DsrcConstants::maxMsgSize;
    std::vector<uint8_t> buf(bufSize, 0);
    /// dsrcFrameOut to store UPER decoding result
    Frame_element_t dsrcFrameOut;

    string output{};
    size_t cnt = spatPayload.length() / 2;

    for (size_t i = 0; cnt > i; ++i)
    {
        uint32_t s = 0;
        std::stringstream ss;
        ss << std::hex << spatPayload.substr(i * 2, 2);
        ss >> s;

        output.push_back(static_cast<unsigned char>(s));
    }

    size_t index = 0;
    for (std::vector<uint8_t>::iterator it = buf.begin(); it != buf.end() && index < output.size(); ++it)
    {
        *it = output[index];
        index++;
    }
    size_t payload_size = output.size();

    if (payload_size > 0 && (AsnJ2735Lib::decode_msgFrame(&buf[0], payload_size, dsrcFrameOut) > 0) && (dsrcFrameOut.dsrcMsgId == MsgEnum::DSRCmsgID_spat))
    {
        SPAT_element_t &spatOut = dsrcFrameOut.spat;

        Json::Value jsonObject;
        Json::StreamWriterBuilder builder;
        builder["commentStyle"] = "None";
        builder["indentation"] = "";
        int currVehPhaseState{};

        jsonObject["MsgType"] = "SPaT";
        jsonObject["Timestamp_verbose"] = getVerboseTimestamp();
        jsonObject["Timestamp_posix"] = getPosixTimestamp();
        jsonObject["Spat"]["intersectionState"]["regionalID"] = spatOut.regionalId;
        jsonObject["Spat"]["intersectionState"]["intersectionID"] = spatOut.id;
        jsonObject["Spat"]["msgCnt"] = static_cast<unsigned int>(spatOut.msgCnt);
        jsonObject["Spat"]["minuteOfYear"] = spatOut.timeStampMinute;
        jsonObject["Spat"]["msOfMinute"] = spatOut.timeStampSec;
        jsonObject["Spat"]["status"] = spatOut.status.to_string();

        int phaseListIndex = 0;
        for (int i = 0; i < 8; i++)
        {
            if (spatOut.permittedPhases.test(i))
            {
                const auto &phaseState = spatOut.phaseState[i];
                currVehPhaseState = static_cast<unsigned int>(phaseState.currState);

                get_min_max_elapsed_time_in_seconds(spatOut.timeStampMinute, spatOut.timeStampSec, phaseState.startTime, phaseState.minEndTime, phaseState.maxEndTime);

                    jsonObject["Spat"]["phaseState"][phaseListIndex]["phaseNo"] = (i + 1);
                // jsonObject["Spat"]["phaseState"][phaseListIndex]["startTime"] = phaseState.startTime;
                // jsonObject["Spat"]["phaseState"][phaseListIndex]["minEndTime"] = phaseState.minEndTime;
                // jsonObject["Spat"]["phaseState"][phaseListIndex]["maxEndTime"] = phaseState.maxEndTime;
                // jsonObject["Spat"]["phaseState"][phaseListIndex]["elapsedTime"] = -1;

                jsonObject["Spat"]["phaseState"][phaseListIndex]["startTime"] = start_time_s;
                jsonObject["Spat"]["phaseState"][phaseListIndex]["minEndTime"] = min_end_time_s;
                jsonObject["Spat"]["phaseState"][phaseListIndex]["maxEndTime"] = max_end_time_s;
                jsonObject["Spat"]["phaseState"][phaseListIndex]["elapsedTime"] = elapsed_time_s;

                if (currVehPhaseState == RED)
                    jsonObject["Spat"]["phaseState"][phaseListIndex]["currState"] = "red";

                else if (currVehPhaseState == FLASHING_RED)
                    jsonObject["Spat"]["phaseState"][phaseListIndex]["currState"] = "flashing_red";

                else if (currVehPhaseState == PERMISSIVE_GREEN)
                    jsonObject["Spat"]["phaseState"][phaseListIndex]["currState"] = "permissive_green";

                else if (currVehPhaseState == PROTECTED_GREEN)
                    jsonObject["Spat"]["phaseState"][phaseListIndex]["currState"] = "protected_green";

                else if (currVehPhaseState == PERMISSIVE_YELLOW)
                    jsonObject["Spat"]["phaseState"][phaseListIndex]["currState"] = "permissive_yellow";

                else if (currVehPhaseState == PROTECTED_YELLOW)
                    jsonObject["Spat"]["phaseState"][phaseListIndex]["currState"] = "protected_yellow";

                phaseListIndex += 1;
            }
        }

        jsonString = Json::writeString(builder, jsonObject);
    }

    double currentTime = static_cast<double>(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()));
    cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Decoded SPaT Json is following: \n"
         << jsonString << endl;

    return jsonString;
}

string MsgDecoder::bsmDecoder(string bsmPayload)
{
    BasicVehicle basicVehicle;
    string jsonString{};

    /// buffer to hold message payload
    size_t bufSize = DsrcConstants::maxMsgSize;
    std::vector<uint8_t> buf(bufSize, 0);
    /// dsrcFrameOut to store UPER decoding result
    Frame_element_t dsrcFrameOut;

    string output{};
    size_t cnt = bsmPayload.length() / 2;

    for (size_t i = 0; cnt > i; ++i)
    {
        uint32_t s = 0;
        std::stringstream ss;
        ss << std::hex << bsmPayload.substr(i * 2, 2);
        ss >> s;
        output.push_back(static_cast<unsigned char>(s));
    }

    size_t index = 0;
    for (std::vector<uint8_t>::iterator it = buf.begin(); it != buf.end() && index < output.size(); ++it)
    {
        *it = output[index];
        index++;
    }
    size_t payload_size = output.size();
    if (payload_size > 0 && (AsnJ2735Lib::decode_msgFrame(&buf[0], payload_size, dsrcFrameOut) > 0) && (dsrcFrameOut.dsrcMsgId == MsgEnum::DSRCmsgID_bsm))
    {
        BSM_element_t &bsmOut = dsrcFrameOut.bsm;
        basicVehicle.setTemporaryID(bsmOut.id);
        basicVehicle.setSecMark_Second((bsmOut.timeStampSec) / 1000.0);
        basicVehicle.setPosition(DsrcConstants::damega2unit<int32_t>(bsmOut.latitude), DsrcConstants::damega2unit<int32_t>(bsmOut.longitude), DsrcConstants::deca2unit<int32_t>(bsmOut.elevation));
        basicVehicle.setSpeed_MeterPerSecond(round(DsrcConstants::unit2kph<uint16_t>(bsmOut.speed) * KPH_TO_MPS_CONVERSION));
        basicVehicle.setHeading_Degree(round(DsrcConstants::unit2heading<uint16_t>(bsmOut.heading)));
        basicVehicle.setType("0");
        basicVehicle.setLength_cm(bsmOut.vehLen);
        basicVehicle.setWidth_cm(bsmOut.vehWidth);
        jsonString = basicVehicle.basicVehicle2Json();
    }

    // double currentTime = static_cast<double>(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()));
    // cout << "[" << fixed << showpoint << setprecision(2) << currentTime << "] Decoded BSM Json is following: \n" << jsonString << endl;
    return jsonString;
}

void MsgDecoder::get_min_max_elapsed_time_in_seconds(int minute_of_the_year, int ms_of_minute, double start_time, double min_end_time, double max_end_time)
{
    // Small epsilon (1 ms) so values at the exact threshold don't flicker to negative due to jitter
    const double EPS = 1e-3;

    // Current time in seconds since start of the hour
    double now_sec = (minute_of_the_year % 60) * 60.0 + (ms_of_minute / 1000.0);

    // Convert tenths of a second to seconds (inputs are in 0.1s per J2735)
    double min_end_abs = min_end_time / 10.0;
    double max_end_abs = max_end_time / 10.0;

    // Remaining times (never negative), with small epsilon for stability
    min_end_time_s = std::max(0.0, (min_end_abs - now_sec) + EPS);
    max_end_time_s = std::max(0.0, (max_end_abs - now_sec) + EPS);

    // Start and elapsed
    if (start_time >= 0.0 && start_time != 36001.0)
    {
        start_time_s = start_time / 10.0;

        // Hour wrap: if start appears after "now", assume it began in the previous hour
        if (start_time_s > now_sec)
            start_time_s -= 3600.0;

        elapsed_time_s = std::max(0.0, now_sec - start_time_s);
    }

    else
    {
        start_time_s = -1.0;
        elapsed_time_s = -1.0;
    }
}

MsgDecoder::~MsgDecoder()
{
}
