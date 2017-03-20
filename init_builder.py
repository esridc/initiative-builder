from arcgis.gis import GIS
import requests
import json
import os
import itertools
import argparse
from tqdm import tqdm
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def generateToken(user, passw):
        """
        Generate Token generates an access token in exchange for \
        user credentials that can be used by clients when working with the ArcGIS Portal API:
        http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000m5000000
        """
        url = "{}/sharing/rest/generateToken".format(args.o)
        data = {'username': user,
                'password': passw,
                'referer': "https://www.arcgis.com",
                'f': 'json'}
        return requests.post(url, data, verify=False).json()['token']


'''this function accepts a dasherized string or a list of dasherized strings,
converts them to camel case, and returns them as either a string or a list of
strings. '''


def dash_to_camel(dash):
    new_tag = []
    new_tag_multi = []
    if type(dash) == list:
        for item in dash:
            if '-' in item:
                temp = item.split('-')
                for word in temp:
                    if temp.index(word) == 0:
                        new_tag.append(word.lower())
                    else:
                        new_tag.append(word.capitalize())
                new_tag_multi.append(''.join(new_tag))
                new_tag = []
            else:
                return "invalid string"
        return new_tag_multi
    else:
        if '-' in dash:
            dash = dash.split('-')
            for word in dash:
                if dash.index(word) == 0:
                    new_tag.append(word.lower())
                else:
                    new_tag.append(word.capitalize())
            return ''.join(new_tag)
        else:
            return


def list_json_files(dir):
    """
    This function searches the directory and every subdirectory in it, for valid json files
    and returns a list of all that it finds.
    """
    r = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file[-4:] == 'json' and file != 'empty_initiative.json':
                r.append(os.path.join(root, file))
    return r


def confirm_path(path):
    """
    this function confirms that all directories in a given path exist
    and in the event that they don't it makes them.
    """
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


parser = argparse.ArgumentParser()
parser.add_argument("u", help="username required")
parser.add_argument("p", help="password required")
parser.add_argument("o", help="the organization url")
parser.add_argument("f", help="enter path to the initiatives")
args = parser.parse_args()

# token = generateToken(args.u, args.p)


# creates a GIS object for using the python api
org = GIS(args.o, args.u, args.p)

# opens the empty initiative file and stores it as the variable initiatve_base
with open('{}/empty_initiative.json'.format(args.f)) as empty:
    initiative_base = json.load(empty)


folder_of_initiatives = list_json_files(args.f)


for item in folder_of_initiatives:
    with open(item) as initiativeFile:
        try:
            initiative = json.load(initiativeFile)
        except:
            print(initiative['id'])

# creates ready to publish initiative item files
archiveList = []

for folder in tqdm(folder_of_initiatives):
    archive = {}  # initializing an empty dictionary to store the archive items
    empty = []

    with open(folder) as initiativeFile:
        user_initiative = json.load(initiativeFile)
        try:
            empty.append(initiative_base['tags'])
            empty.append(user_initiative['tags'])
            flat = list(itertools.chain(*empty))
            user_initiative['tags'] = flat
        except:
            pass
    final_initiative = {**initiative_base, **user_initiative}
    final_initiative['data']['values']['steps'] = final_initiative['steps']
    final_initiative['data']['values']['initiativeType'] = 'customInitiative'
    final_initiative.pop('steps', None)

    p = './output/{}/'.format(user_initiative['id'])
    confirm_path(p)

    with open('./output/{}/{}-{}.json'.format(user_initiative['id'], user_initiative['id'], 'en-us'), 'w+') as outfile:

        json.dump(final_initiative['data'], outfile, sort_keys=True, indent=4, ensure_ascii=False)

    x = '{}.json'.format(final_initiative['id'])
    temp = org.content.add(item_properties={"type": final_initiative['type'],
                                            "title": final_initiative['title'],
                                            "typeKeywords": "hubInitiativeTemplate, JavaScript, Ready To Use, {}".format(final_initiative['id']),  # selfConfigured
                                            "tags": "Hub Initiative Template",
                                            "snippet": final_initiative['snippet'],
                                            "description": final_initiative['description'],
                                            "licenseInfo": "CC-BY-SA",  # "licenseInfo": final_initiative['licenseInfo'],
                                            "culture": "en-us",
                                            "access": "org",
                                            "accessInformation": "Esri"}, folder="mp_initiatives")

    # if there's a folder of resources for the initiative, attach those resource items to the initiative
    try:
        resource_files = os.listdir('{}/{}/resources'.format(args.f, final_initiative['id']))

        for item in resource_files:
            temp.resources.add('{}/{}/resources/{}'.format(args.f, final_initiative['id'], item))
            pass
    except:
        pass

    temp.share(everyone=True)

    initiatives = {
        temp['title']: {
            "items": {
                temp['culture']: {
                    "id": temp['id'],
                    "updatedAt": temp['modified']
                }
            }
        }
    }
    archiveList.append(initiatives)

for item in archiveList:

    # pdb.set_trace()
    with open('./archive/dev-initiatives.json', 'w+') as archiveFile:
        json.dump(item, archiveFile, sort_keys=True, indent=4)
