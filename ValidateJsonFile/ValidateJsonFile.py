# Function to validate json files:

# importing enum for enumerations
import enum

# creating enumerations using class
class ValueType(enum.Enum):
    string = 1
    number = 2
    jsonObject = 3


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
    curInd = 1;
    while (curInd < len(subJsonObj)):
        nextPair = getNextPair(curInd, subJsonObj);
        if nextPair[0] is None:
            return [False, nextPair[1]];

        print(nextPair)
        curInd = nextPair[1];

        curInd = getNextCommaOrEndSignIndex(nextPair[1],subJsonObj);
        if curInd == -1:
            errorStr = "getNextCommaOrEndSignIndex() returned -1. Index="+str(nextPair[1])+", subJsonObj="+subJsonObj
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

    curInd = getNextColonSignIndex(curInd+1,jsonobj);
    if curInd == -1:
        errorStr = "Could not find Colon ':' sign. Start Iindex=" + str(curInd) + ",jsonobj=" + jsonobj
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
    errorStr = "";
    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];

        # Continue until encounter the first quote sign "
        if (not foundFirstQuote) and (ch == ' ' or ch == '\t' or ch == '\n' or ch == ''):
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

        if ch == ' ' or ch == '\n':
            continue;
        elif ch == ':':
            return i;
        else:
            return -1;

    return -1;

def getNextValue(curInd , jsonObj):
    value = "";
    foundInd = -1;
    valueType = -1;
    curlyBracketsCount = 0;
    info = "";
    for i in range(curInd,len(jsonObj)):
        ch = jsonObj[i];

        # Looking for the value:
        if valueType == -1 and (ch == ' ' or ch == '\n'):
            continue;

            # String Value - Start
        elif valueType == -1 and ch == '"' :
            info += " Found first quote sign '"' - looking for a String value.'
            valueType = (ValueType.string).value;

        elif valueType == (ValueType.string).value and ch != '"':
            value += ch;

        elif valueType == (ValueType.string).value and ch == '"':
            foundInd = i+1;
            info += " Found second quote sign '"'.'
            info += " Read Value: '" + value + "'. Done"
            break;
            # String Value - End

            # Number Value - Start
        elif (valueType == -1 or valueType == (ValueType.number).value) and ch.isdigit():
            if valueType == -1:
                info += " Found digit - Looking for Number value."
            value += ch;
            valueType = (ValueType.number).value;

        elif valueType == (ValueType.number).value and not ch.isdigit():
            if ch == ',' or ch == ' ' or ch == '\n' or ch == '}':
                foundInd = i;
            else:
                # Bad value case
                info += " Found bad char: '"+ch+"' while reading the number: '"+value+"'.";
                foundInd = -1;

            break;

            # Number Value - End

            # JsonObject Value - Start
        elif (valueType == -1 or valueType == (ValueType.jsonObject).value) and ch == '{':
            if valueType == -1:
                info += " Found '{' - Looking for Json-Object value."
            value += ch;
            valueType = (ValueType.jsonObject).value;
            curlyBracketsCount += 1;

        elif valueType == (ValueType.jsonObject).value and ch != '{' and ch != '}':
            value += ch;

        elif valueType == (ValueType.jsonObject).value and ch == '}':
            value += ch;
            foundInd = i+1;
            curlyBracketsCount -= 1;
            if curlyBracketsCount == 0:
                break;
            # JsonObject Value - End

    validateRes = validateValue(value,valueType,foundInd,curlyBracketsCount)
    if validateRes[0]:
        return [value,foundInd];
    else:
        errorStr = info + " Error: "+validateRes[1];
        return [None,errorStr];


def validateValue(value,valueType,foundInd,curlyBracketsCount):
    if foundInd == -1:
        return [False, "Found index is -1. Could not find value(or end of value)"];

    if valueType == (ValueType.jsonObject).value:
        if curlyBracketsCount != 0:
            return [False, "Curly Brackets is not 0. Not even number of '{' and '}'"];
        else:
            return (validateJsonObject(value));

    return [True,"Value is ok"];



def getNextCommaOrEndSignIndex(curInd,jsonobj):
    if curInd == len(jsonobj):
        return curInd;

    for i in range(curInd,len(jsonobj)):
        ch = jsonobj[i]

        if ch == ' ' or ch == '\n' or ch == '\t':
            continue;
        elif ch == ',':
            return i;
        else:
            return -1;

    # Default value - no comma
    return len(jsonobj);







print("started")
myFile = "D:/aTraining_1.txt"
result = validateJsonFile(myFile)


if result[0]:
    print("Success",result[1])
else:
    print(result[1])
