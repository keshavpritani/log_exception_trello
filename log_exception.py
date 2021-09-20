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

ignore_card_list_name = "Ignore Card List"
ignore_exception_list_name = "Ignore Exceptions List"

list_id = ""
ignore_card_list_id = "612f969406b71889476adc7a"
ignore_exception_list_id = "613a684d015a5d2bb110ec31"

original_query = {
    'key': '6e5c646bcf9f209c9221cd2fd72a18cf',
    'token': '1fd1dce81d58308556244cc30a6554f5e5061a285cef486135e9a19ed31c7f83',
    "fields": ["name"]
}

ignored_cards = set()
ignored_exceptions = set()
already_added_cards = {}

def changeDate():
    global current_date, last_week, d
    d = date.today()
    current_date = d.strftime("%d %B, %Y")
    print("Current Date =", current_date)
    last_week = (d - timedelta(days=7)).strftime("%d %B, %Y")
    print("last_week =", last_week)
    ignored_cards.clear()
    ignored_exceptions.clear()
    already_added_cards.clear()
    fetchIds()


def createNewList():
    query={}
    global last_week_id

    if(last_week_id != ""):
        print("Deleting", last_week, "list")
        query["value"] = "true"
        response = requests.request(
            "PUT",
            lists_url.format(last_week_id, "closed"),
            params=original_query
        )
        last_week_id = ""
        del query["value"]

    query["name"] = current_date
    query["idBoard"] = board_id
    response = requests.request(
        "POST",
        base_list_url,
        params={**original_query, **query}
    )
    print("Crearted new List for Current Date")

    a = json.loads(response.text)
    return a['id']


def updateCard(card_id):
    query={"fields": ["desc"]}
    # print(card_id)
    print("Card for Exception Already Exists")
    # get the card id and update the card description
    response = requests.request(
        "GET",
        base_card_url+"/{}".format(card_id),
        params={**original_query, **query}
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
    query["pos"]="top"
    response = requests.request(
        "PUT",
        base_card_url+"/{}".format(card_id),
        params={**original_query, **query}
    )
    if(200 <= response.status_code < 300):
        print("Card's Count Incremented")
    else:
        print("Error while Updating Card")


def createCard(program_name, exception_name, card_desc, exceptions_list):
    global list_id, ignore_card_list_id, base_card_url, d, current_date

    exception_name = exception_name.strip(" ")
    #print("CREATE CARD CALLED")
    if(d != date.today()):
        print("New Day")
        list_id = ""
        last_week_id = ""
        changeDate()

    if(exception_name in ignored_cards):
        print("Card Ignored")
        return

    response = requests.request(
        "GET",
        lists_url.format(ignore_exception_list_id, "cards"),
        params=original_query
    )

    ignored_exceptions_list = json.loads(response.text)

    for x in ignored_exceptions_list:
        ignored_exceptions.add(x['name'])


    if (all(item in ignored_exceptions for item in exceptions_list)):
        print("Exceptions Ignored")
        return

    response = requests.request(
        "GET",
        lists_url.format(ignore_card_list_id, "cards"),
        params=original_query
    )

    ignored_cards_list = json.loads(response.text)

    for x in ignored_cards_list:
        if x['name'].find(exception_name) != -1:
            ignored_cards.add(exception_name)
            print("Card Ignored")
            return

    #print(already_added_cards)
    exception_title = program_name + " - "  + exception_name
    if exception_title in already_added_cards:
        updateCard(already_added_cards[exception_title])
    elif (createCardHelper(exception_title, card_desc, exceptions_list, 1)):
        print("Created new Exception Card")
    else:
        print("Error while Creating Card")


def createCardHelper(exception_title, card_desc, exceptions_list, count):
    global list_id
    query={}
    query["name"] = exception_title
    query["idList"] = list_id
    query["desc"] = "Count : 1\n" + "Exceptions - " + ", ".join(exceptions_list) + "\n\n"  + card_desc
    query["pos"]="top"
    response = requests.request(
        "POST",
        base_card_url,
        params={**original_query, **query}
    )

    if(200 <= response.status_code < 300):
        already_added_cards[exception_title] = json.loads(response.text)['id']
        return True
    elif (count <= 4):
        return createCardHelper(exception_title, card_desc[:-len(card_desc)/4], exceptions_list, count + 1)


def fetchIds():
    # print(url)
    global list_id, last_week_id
    response = requests.request(
        "GET",
        url,
        params=original_query
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
        params=original_query
    )

    a = json.loads(response.text)
    # pp.pprint(a)

    for x in a:
        t = x['name'].split("-")[-1].strip(" ")
        already_added_cards[t] = x['id']
    # print(already_added_cards)

    response = requests.request(
        "GET",
        lists_url.format(ignore_card_list_id, "cards"),
        params=original_query
    )

    ignored_cards_list = json.loads(response.text)

    for x in ignored_cards_list:
        ignored_cards.add(x['name'].split("-")[-1].strip(" "))

    response = requests.request(
        "GET",
        lists_url.format(ignore_exception_list_id, "cards"),
        params=original_query
    )

    ignored_exceptions_list = json.loads(response.text)

    for x in ignored_exceptions_list:
        ignored_exceptions.add(x['name'])


def getBoardAndIgnoreListId():
    # find the board id and ignore list id by querying the api
    global board_id, ignore_card_list_id
    query={"fields": ["name", "idBoard"]}
    response = requests.request(
        "GET",
        url,
        params={**original_query, **query}
    )
    a = json.loads(response.text)
    print("Board id = ", a[0]['idBoard'])
    # find the ignore list id
    for x in a:
        if x['name'] == ignore_card_list_name:
            print("Ignore Card List Id = ", x['id'])
        if x['name'] == ignore_exception_list_name:
            print("Ignore Exception List Id = ", x['id'])


# check if the file has run by __main__ or imported
if __name__ == "__main__":
    getBoardAndIgnoreListId()
else:
    changeDate()
