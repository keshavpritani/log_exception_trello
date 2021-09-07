import requests
import json
# import pprint
from datetime import date, timedelta

# pp = pprint.PrettyPrinter()
d = ""
current_date = ""
last_week = ""
last_week_id = ""


board_id = "612f9677e58e0a87b80c3c40"
url = "https://api.trello.com/1/boards/wavZwmwo/lists"

base_list_url = "https://api.trello.com/1/lists"
lists_url = base_list_url+"/{}/{}"

base_card_url = "https://api.trello.com/1/cards"

ignore_list_name = "Ignore Card List"

list_id = ""
ignore_list_id = "612f969406b71889476adc7a"

original_query = {
    'key': '6e5c646bcf9f209c9221cd2fd72a18cf',
    'token': '1fd1dce81d58308556244cc30a6554f5e5061a285cef486135e9a19ed31c7f83',
    "fields": ["name"]
}

ignore_exceptions = []
already_added_exceptions = {}

def changeDate():
    global current_date, last_week, d
    d = date.today()
    current_date = d.strftime("%d %B, %Y")
    print("Current Date =", current_date)
    last_week = (d - timedelta(days=7)).strftime("%d %B, %Y")
    print("last_week =", last_week)
    ignore_exceptions = []
    already_added_exceptions = {}
    fetchIds()


def createNewList():
    global last_week_id
    query={}

    if(last_week_id != ""):
        print("Deleting", last_week, "list")
        query["value"] = "true"
        response = requests.request(
            "PUT",
            lists_url.format(last_week_id, "closed"),
            params={original_query | query}
        )
        last_week_id = ""
        del query["value"]

    query["name"] = current_date
    query["idBoard"] = board_id
    response = requests.request(
        "POST",
        base_list_url,
        params={original_query | query}
    )
    print("Crearted new List for Current Date")

    del query["name"]
    del query["idBoard"]

    a = json.loads(response.text)
    return a['id']

def updateCard(card_id):
    query={}
#    print(card_id)
    print("Card for Exception Already Exists")
    # get the card id and update the card description
    query["fields"].append("desc")
    response = requests.request(
        "GET",
        base_card_url+"/{}".format(card_id),
        params={original_query | query}
    )
    a = json.loads(response.text)
    # pp.pprint(a)
    # split the card description and get the count
    card_desc = a['desc'].split("\n")
    count = int(card_desc[0].split(":")[1])
    count += 1
    card_desc[0] = "Count: {}".format(count)
    card_desc = "\n".join(card_desc)
    # print(card_desc)
    # update the card description
    query["desc"] = card_desc
    response = requests.request(
        "PUT",
        base_card_url+"/{}".format(card_id),
        params={original_query | query}
    )
    query["fields"].remove("desc")
    del query["desc"]
    print("Card's Count Incremented")

def createCard(program_name, exception_name, card_desc, exceptions_list):
    global list_id, ignore_list_id, base_card_url, d, current_date
    query={}

    exception_name = exception_name.strip(" ")
    #print("CREATE CARD CALLED")
    if(d != date.today()):
        print("New Day")
        list_id = ""
        last_week_id = ""
        changeDate()

    if(exception_name in ignore_exceptions):
        print("Exception Igonred")
        return

    response = requests.request(
        "GET",
        lists_url.format(ignore_list_id, "cards"),
        params={original_query | query}
    )

    ignore_cards_list = json.loads(response.text)

    for x in ignore_cards_list:
        if x['name'].find(exception_name) != -1:
            ignore_exceptions.append(exception_name)
            print("Exception Igonred")
            return

    #print(already_added_exceptions)

    if exception_name in already_added_exceptions:
        #print("hello")
        updateCard(already_added_exceptions[exception_name])
        return

    query["name"] = program_name + " - "  + exception_name
    query["idList"] = list_id
    query["desc"] = "Count : 1\n" + "Exceptions - " + ", ".join(exceptions_list) + "\n\n"  + card_desc
    query["pos"]="top"
    response = requests.request(
        "POST",
        base_card_url,
        params={original_query | query}
    )
    #print("after")
    if(200 <= response.status_code < 300):
        already_added_exceptions[exception_name] = json.loads(response.text)['id']
        print("Created new Exception Card")
    else:
        print("Error while Creating Card")

    del query["name"]
    del query["idList"]
    del query["desc"]
    del query["pos"]

def fetchIds():
    # print(url)
    global list_id, last_week_id
    query={}
    response = requests.request(
        "GET",
        url,
        params={original_query | query}
    )
    a = json.loads(response.text)
    # pp.pprint(a)
    for x in a:
        if x['name'] == current_date:
            print("List for Current Date Already Exists")
            list_id = x['id']
        if x['name'] == last_week:
            last_week_id = x['id']

    #print(list_id)
    #print(last_week_id)
    if list_id == "":
        list_id = createNewList()

    response = requests.request(
        "GET",
        lists_url.format(list_id, "cards"),
        params={original_query | query}
    )

    a = json.loads(response.text)
    # pp.pprint(a)

    for x in a:
        t = x['name'].split("-")[-1].strip(" ")
        already_added_exceptions[t] = x['id']
#    print(already_added_exceptions)

    response = requests.request(
        "GET",
        lists_url.format(ignore_list_id, "cards"),
        params={original_query | query}
    )

    ignore_cards_list = json.loads(response.text)

    for x in ignore_cards_list:
        ignore_exceptions.append(x['name'].split("-")[-1].strip(" "))

def getBoardAndIgnoreListId():
    # find the board id and ignore list id by querying the api
    global board_id, ignore_list_id
    query={}
    query["fields"].append("idBoard")
    response = requests.request(
        "GET",
        url,
        params={original_query | query}
    )
    a = json.loads(response.text)
    print("Board id = ", a[0]['idBoard'])
    # find the ignore list id
    for x in a:
        if x['name'] == ignore_list_name:
            print("List Id = ", x['id'])
            break
    else:
        print("Ignore List Not Found")

    query["fields"].remove("idBoard")


# check if the file has run by __main__ or imported
if __name__ == "__main__":
    getBoardAndIgnoreListId()
else:
    changeDate()

