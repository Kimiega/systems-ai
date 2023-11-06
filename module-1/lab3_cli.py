from swiplserver import PrologMQI, PrologThread, create_posix_path
import re

hint_help = """
Что у меня есть?
Хочу добавить: item, ..., item.
Хочу выкинуть: item, ..., item.
Что могу скрафтить?
Что могу выплавить?
Хочу скрафтить: item, ..., item.
Хочу выплавить: item, ..., item.
Все рецепты
Все предметы
Что мне нужно сделать для крафта: item.
"""

get_inventory_query = re.compile(r'Что у меня есть?')
add_items_to_inventory_query = re.compile(r'Хочу добавить: (.*,){0,}(.*)\.')
remove_items_from_inventory_query = re.compile(r'Хочу выкинуть: (.*,){0,}(.*)\.')
available_crafts_query = re.compile(r'Что могу скрафтить?')
available_furnance_crafts_query = re.compile(r'Что могу выплавить?')
craft_query = re.compile(r'Хочу скрафтить: (.*,){0,}(.*)\.')
furnance_craft_query = re.compile(r'Хочу выплавить: (.*,){0,}(.*)\.')
all_recipes_query = re.compile(r'Все рецепты')
all_items_query = re.compile(r'Все предметы')
guide_to_craft_certain_item_query = re.compile(r'Что мне нужно сделать для крафта: \w+.')

user_inventory = []


def analyse_query(query):
    if query == "exit" or query == "quit":
        print("Goodbye!")
        exit(0)
    if query == "help":
        return hint_help

    q = get_inventory_query.search(query)
    if q:
        return get_inventory()

    q = add_items_to_inventory_query.search(query)
    if q:
        return add_items_to_inventory(get_items_from_query(q[0], 15))

    q = remove_items_from_inventory_query.search(query)
    if q:
        return remove_items_from_inventory(get_items_from_query(q[0], 15))

    q = available_crafts_query.search(query)
    if q:
        return available_crafts()

    q = available_furnance_crafts_query.search(query)
    if q:
        return available_furnance_crafts()

    q = all_recipes_query.search(query)
    if q:
        return all_recipes()

    q = craft_query.search(query)
    if q:
        return craft(get_items_from_query(q[0], 16))

    q = furnance_craft_query.search(query)
    if q:
        return furnance_craft(get_items_from_query(q[0], 16))

    q = all_items_query.search(query)
    if q:
        return all_items()

    q = guide_to_craft_certain_item_query.search(query)
    if q:
        larr = get_items_from_query(q[0], 34)
        if len(larr):
            return guide_to_craft_certain_item(larr[0])

    return "Wrong command\nType 'help'\n"


def get_items_from_query(query, start_index):
    items = re.findall(r'[a-zA-Zа-яА-ЯёЁ]\w*[^\.,]*', query[start_index:])
    return items


def get_inventory():
    return "Your inventory has: " + str(user_inventory)


def add_items_to_inventory(items):
    global user_inventory
    result = ""
    for item in items:
        res = prolog.query(f'get_item({item}, {user_inventory}, X)')
        if not res:
            result += item + " doesn't exist in db\n"
        else:
            user_inventory = res[0]['X']
    return result + "Inventory now: " + str(user_inventory)


def remove_items_from_inventory(items):
    global user_inventory
    for item in items:
        res = prolog.query(f'remove_item({item}, {user_inventory}, Inv)')
        user_inventory = res[0]['Inv']
    return "Inventory now: " + str(user_inventory)


def available_crafts():
    res = prolog.query(f'available_crafts({user_inventory}, Items)')
    if not res:
        return "You can't craft anything\n"
    result = "Available items to craft:\n"
    for i in res:
        result += str(i['Items']) + "\n"
    return result


def available_furnance_crafts():
    res = prolog.query(f'available_furnance_craft({user_inventory}, Items)')
    if not res:
        return "You can't meltdown anything\n"
    result = "Available items to be meltdown:\n"
    for i in res:
        result += str(i['Items']) + "\n"
    return result


def all_recipes():
    res = prolog.query(f'recipe(X, Y)')
    result = "All recipes:\n"
    for recipe in res:
        result += str(recipe['X']) + " -> " + str(recipe['Y']) + "\n"
    return result


def craft(items):
    global user_inventory
    result = ""
    for item in items:
        res = prolog.query(f'craft({user_inventory}, {item}, Inv)')
        if not res:
            result += f"Can't be crafted: {item}\n"
        else:
            user_inventory = res[0]['Inv']
            result += f"Was crafted: {item}\n"
    return result


def furnance_craft(items):
    global user_inventory
    result = ""
    for item in items:
        res = prolog.query(f'member(coal, {user_inventory})')
        if not res:
            result += "Coal has run out\n"
            break
        res = prolog.query(f'meltdown({user_inventory}, {item}, Inv)')
        if not res:
            result += f"Can't be melted down: {item}\n"
        else:
            user_inventory = res[0]['Inv']
            result += f"Was melted down: {item}\n"
    return result


def all_items():
    res = prolog.query(f'item(X)')
    result = "All items:\n"
    for item in res:
        result += str(item['X']) + "\n"
    return result


def guide_to_craft_certain_item(item):
    global user_inventory
    result = ""
    stack = []
    items_to_get = []
    items_to_craft = []
    items_to_meltdown = []
    stack.append(item)
    u_inventory = user_inventory[:]
    while len(stack) > 0:
        item = stack.pop()
        res = prolog.query(f'can_craft(Req_items, {item})')
        if not res:
            res2 = prolog.query(f'can_melted(Req_items, {item})')
            if not res2:
                items_to_get.append(item)
               # res3 = prolog.query(f'recipe(X, Items), member({item}, X)')
               # arr4 = res3[0]['Items']
               # arr4.pop()
            else:
                items_to_meltdown.append(item)
                arr = res2[0]['Req_items']
                arr2 = []
                x = arr
                while x != '_':
                    x = x['args']
                    arr2.append(x[0])
                    x = x[1]

                for i in arr2:
                    if i in u_inventory:
                        u_inventory.remove(i)
                    else:
                        stack.append(i)
        else:
            items_to_craft.append(item)
            arr = res[0]['Req_items']
            arr2 = []
            x = arr
            while x != '_':
                x = x['args']
                arr2.append(x[0])
                x = x[1]

            for i in arr2:
                if i in u_inventory:
                    u_inventory.remove(i)
                else:
                    stack.append(i)

    result += "You need to get:\n"
    for i in items_to_get[::-1]:
        result += i + "\n"
    result += "\nYou need to meltdown:\n"
    for i in items_to_meltdown[::-1]:
        result += i + "\n"
    result += "\nYou need to craft:\n"
    for i in items_to_craft[::-1]:
        result += i + "\n"
    return result


with PrologMQI() as mqi:
    with mqi.create_thread() as prolog:
        path = create_posix_path("lab1_db.pl")
        prolog.query(f'consult("{path}").')

        print("type 'help' for information\n")

        while (True):
            query = input()

            result = analyse_query(query)

            print(result)
