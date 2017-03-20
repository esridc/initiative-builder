This script uses the ArcGIS Python 3 API* to automate the publishing of initiative items in a given development environment. As it stands now, the script requires parameters, that are passed in from the command line. `u` is the arcgis username, `p` is the user password, `o` is the portal url and `f` is the local path to the directory where the initiative json files are stored


*Specifically you'll have to install the python api from source, as the current public release of the api is missing the update item resources functionality.


Example:
`python3 init_builder.py <username> <password> <portal> <folder>`


The script first gathers all the initiative files in the folder that was passed in as an argument and stores them in a list named `folders_of_initiatives`

The next step in the process is that the it takes every initiative in that list, and constructs items with the required values for each, then uses the python api's `add` method to publish those items to the dev environment passed in as an argument.

After publishing the item, the script then looks for a folder of resources for that initiative, and if it finds one, it updates the newly created item with those resources. We can't attach the resources during the initial publish, because you can't attach resources to an item that hasn't been created yet.

Finally the script writes two files to disk. It saves a copy of the data json to `/output/<initiative name>` and  writes a log of the items it's published and saves it to the `/archive` directory. 



Issues:

I'm still having issues publishing the data json with the item. What this mean is that I get what appears to be correct agol item that I can view the item page for, and which also populates the initiative gallery with a new initiative card. The images resources attached successfully to the item is indicated by the gallery card's icon being displayed on the card, or by the `size` key on the json screenshot.




The API docs say that to publish the data, call the `add` method of the object, and pass in an "optional string, either a path or URL to the data". No variation of this as I understand it, has been successful for me to date. This means when I click on one of the newly created gallery cards, I receive an error message.

The url that the card is attempting to link to follows the format `https://opendatadev.arcgis.com/admin/initiatives/gallery/<item id>`

In Dave's javascript/node code, he stringifies the json and updates the text property with that string. https://github.com/ArcGIS/hub-automation/blob/master/lib/item.js#L85-L90

My attempts to do similar have also been unsuccessful, but it's possible my understanding of how to do this with the python api is flawed. For instance, I don't believe the python api gives me access to the text property.
