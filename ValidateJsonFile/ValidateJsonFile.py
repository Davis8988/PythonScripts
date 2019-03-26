# Function to validate json files:

import enum # For ValueType as enumerations
import ast # For converting string representation of list to actual list variable

# creating enumerations using class
class ValueType(enum.Enum):
    string = 1
    number = 2
    list = 3
    jsonObject = 4

spaceChars = [""," ","\n","\t"]


def validateJsonFile(jsonFilePath):
    print("Validating json file at: ",jsonFilePath)
    try:
        print("Attempting to read the json file")
        jsonFile = open(jsonFilePath, 'r')

        jsonFileContent = jsonFile.read()
        print("Read Successfuly")

        return validateJsonObject(jsonFileContent);




    except FileNotFoundError:
        print("Error. File to read not found at:",jsonFilePath)
    except IOError:
        print("Error. Unable to read file:",jsonFilePath)
    except:
        print("Unhandled Exception while attempting to read the file:",jsonFilePath)

    return [False, "Could not read json file"];


def validateJsonObject(jsonobj):
    if jsonobj is None:
        return [False, "Param jsonobj is Null"];
    if not type(jsonobj) == str:
        return [False, "Param jsonobj is of type: "+str(type(jsonobj))+" instead of a String type"];

    # Trim the string:
    jsonobj = jsonobj.strip()

    if not jsonobj[0] == "{":
        return [False, "Param jsonobj doesn't start with a '{' sign"];
    if not jsonobj[-1] == "}":
        return [False, "Param jsonobj doesn't end with a '}' sign"];
    if len(jsonobj) == 2:
        return [True, jsonobj]

    subJsonObj = jsonobj[1:-1]
    curInd = 0;
    while (curInd < len(subJsonObj)):
        nextPair = getNextPair(curInd, subJsonObj);
        if nextPair[0] is None:
            return [False, nextPair[1]];

        print(nextPair)
        curInd = nextPair[1];
        getCommaResult = getNextCommaOrEndSignIndex(curInd+1,subJsonObj);

        curInd = getCommaResult[0]
        if curInd == -1:
            errorStr = getCommaResult[1];
            return [False , errorStr];

        curInd += 1;

    return [True, "Json Object is Valid"];


def getNextPair(curInd , jsonobj):
    pair = []

    key = getNextKey(curInd,jsonobj);
    if key[0] is None:
        errorStr = key[1]
        return [None,errorStr];

    pair.append(key[0]);
    curInd = key[1];

    colonResult = getNextColonSignIndex(curInd+1,jsonobj);
    curInd = colonResult[0]
    if curInd == -1:
        errorStr = "Could not find Colon ':' sign. "+colonResult[1]+"\nStart Iindex=" + str(curInd) + ",jsonobj=" + jsonobj
        return [None, errorStr];

    value = getNextValue(curInd+1,jsonobj)
    if value[0] is None:
        errorStr = value[1];
        return [None, errorStr];

    pair.append(value[0])
    curInd = value[1];
    return [pair,curInd];


def getNextKey(curInd , jsonObj):
    key = "";
    foundInd = -1;
    foundFirstQuote = False;
    errorStr = "Could not get next key";
    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];

        # Continue until encounter the first quote sign "
        if (not foundFirstQuote) and ch in spaceChars:
            continue;

        # When found - mark 'foundFirstQuote'
        elif ch == '"' and (not foundFirstQuote):
            foundFirstQuote = True;

        # Everything inside first quite and second quite is a key
        #   so add it to a string variable: key
        elif foundFirstQuote and ch != '"':
            key += ch;

        # If found the second quote sign "  - mark found index, and break the loop
        elif ch == '"' and foundFirstQuote:
            foundInd = i;
            break;

        else:
            errorStr = " Found bad char: '"+ch+"' while attempting to get next Key. At index: "+str(curInd) + ",jsonObj=" + jsonObj;
            break;

    if foundInd != 1 and type(key) == str and len(key) > 0:
        return [key,foundInd]
    else:
        return [None,errorStr]

def getNextColonSignIndex(curInd , jsonObj):

    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];

        if ch in spaceChars:
            continue;
        elif ch == ':':
            info = ""
            return [i,info];
        else:
            info = "Found Bad Char: "+ch;
            break;

    return [-1,info];

def getNextValue(curInd , jsonObj):
    readResult = [];
    valueType = -1;
    info = "";
    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];

        # Looking for the value:
        if valueType == -1 and ch in spaceChars:
            continue;

            # String Value
        elif valueType == -1 and ch == '"' :
            valueType = (ValueType.string).value;
            readResult = readStringValue(i , jsonObj)
            break;

            # Number Value
        elif (valueType == -1) and ch.isdigit():
            info += " Found digit - Looking for Number value."
            valueType = (ValueType.number).value;
            readResult = readNumberValue(i, jsonObj)
            break;

            # List Value
        elif valueType == -1 and ch == '[':
            valueType = (ValueType.list).value;
            readResult = readListValue(i, jsonObj);
            break;

            # JsonObject Value
        elif valueType == -1 and ch == '{':
            valueType = (ValueType.jsonObject).value;
            readResult = readJsonObjectValue(i, jsonObj);
            break;
        else:
            continue;

    foundInd = readResult[0];
    value = readResult[1];
    info += readResult[2];
    if foundInd == -1:
        errorStr = info + " Error while trying to read value: " + value
        return [None, errorStr];

    validateResult = validateValue(value,valueType,foundInd)

    if validateResult[0] == True:
        return [value,foundInd];
    else:
        errorStr = info + " Error: "+validateResult[1];
        return [None,errorStr];

def readStringValue(curInd, jsonObj):
    value = "";
    info = "";
    foundFirstQoute = False
    foundInd = -1;
    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];
        if not foundFirstQoute and ch in spaceChars:
            continue;

        elif not foundFirstQoute and ch == '"':
            info += " Found first quote sign '"' - looking for a String value.'
            foundFirstQoute = True;
            continue;

        elif foundFirstQoute and not ch == '"':
            value += ch;

        elif foundFirstQoute and ch == '"':
            foundInd = i;
            break;

    return [foundInd , value , info]

def readNumberValue(curInd, jsonObj):
    value = "";
    info = "";
    foundInd = -1;
    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];
        if ch.isdigit():
            foundInd = i
            value += ch;
        elif (ch in spaceChars) or ch == '}' or ch == ',':
            break;
        else:
            # Bad value case
            info += " Found bad char: '" + ch + "' while reading the number: '" + value + "'.";
            foundInd = -1;
            break;

    return [foundInd , value , info]

def readJsonObjectValue(curInd, jsonObj):
    value = "";
    info = "";
    foundInd = -1;
    curlyBracketsCount = 0;
    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];

        value += ch;

        if ch == '{':
            curlyBracketsCount += 1;
        elif ch == '}':
            curlyBracketsCount -= 1;
            if curlyBracketsCount == 0:
                foundInd = i;
                break;

    return [foundInd , value , info]

def readListValue(curInd, jsonObj):
    value = "";
    info = "";
    foundInd = -1;
    squareBracketsCount = 0;
    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];

        value += ch;

        if ch == '[':
            squareBracketsCount += 1;
        elif ch == ']':
            squareBracketsCount -= 1;
            if squareBracketsCount == 0:
                foundInd = i;
                break;

    return [foundInd , value , info]

def validateValue(value,valueType,foundInd):
    if foundInd == -1:
        return [False, "Found index is -1. Could not find value(or end of value)"];

    if valueType == (ValueType.jsonObject).value:
        return (validateJsonObject(value));

    if valueType == (ValueType.list).value:
        return (validateListValue(value));

    return [True,"Value is ok"];


def validateListValue(value):
    if len(value) == 2:
        return [True, "List is empty"]

    try:
        validateRes = ast.literal_eval(value)
        return [True, ""]
    except SyntaxError:
        info = "List: "+value+"\nis of wrong syntax. Correct list values syntax is: [\"StringVal\" , Digits, True, False, [AnotherList] ]"
        return [False, info]
    except:
        info = "Unknown error occured while validating list: "+value
        return [False, info]




def getNextCommaOrEndSignIndex(curInd,jsonobj):
    for i in range(curInd,len(jsonobj)):
        ch = jsonobj[i]

        if ch in spaceChars:
            continue;
        elif ch == ',':
            # Check if have enough chars for another key
            if (len(jsonobj) - i) >= 5:
                info = ""
                return [i, info];
            else:
                info = "Found comma sign ',' but not enough space for another key after it before the end of the string."
                return [-1, info];
        else:
            info = "Found Bad Char: "+ch;
            return [-1, info];

    # Default value - no comma
    info = "End of object - No comma found after char index "+str(curInd)+"\nObject: " + jsonobj;
    return [len(jsonobj), info];







print("started")
myFile = "D:/aTraining_1.txt"
result = validateJsonFile(myFile)


if result[0]:
    print("Success",result[1])
else:
    print(result[1])
