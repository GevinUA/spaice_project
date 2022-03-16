import sys
import time
import asyncio

inifinity = float("inf")


# async function which writes the command history to the file
async def handle_command_history(f, string_1, string_2):
    f.write(time.asctime()+"---------"+string_1)
    f.write(time.asctime()+"---------"+string_2)


# all general "ADD" command comes here
def handle_all_add(product_dict, warehouse_limit_dict, args_list):
    # depends on different adding operation, perform different adding function
    if(args_list[1].upper() == "PRODUCT"):
        handle_add_product(product_dict, args_list)
    elif(args_list[1].upper() == "WAREHOUSE"):
        handle_add_warehouse(warehouse_limit_dict, args_list)
    else:
        #print("invalid args, please try again.")
        print("invalid args, please try again.")


# all general "list" command comes here
def handle_all_list(product_dict, warehouse_limit_dict,
                    warehouse_product_dict, args_list):
    # depends on different list operation, perform different list function
    if(args_list[1].upper() == "PRODUCTS"):
        handle_list_products(product_dict)
    elif(args_list[1].upper() == "WAREHOUSES"):
        handle_list_warehouses(warehouse_limit_dict)
    elif(args_list[1].upper() == "WAREHOUSE"):
        handle_list_single_warehouse(
            warehouse_limit_dict, warehouse_product_dict, product_dict, args_list)
    else:
        print("invalid args, please try again.")


# adding the product
def handle_add_product(product_dict, args_list):
    product_name, sku = args_list[2].split(" ")
    if sku in product_dict:
        print(("ERROR ADDING PRODUCT, PRODUCT with SKU {sku} ALREADY EXISTS").format(
            sku=sku))
        return
    product_name = product_name.replace('"', '')
    product_dict[sku] = product_name


# adding the warehouse
def handle_add_warehouse(warehouse_limit_dict, args_list):
    if(len(args_list) <= 2):
        print("please give specific warehouse adding number")
        return
    check_limit = args_list[2].split(" ")
    if (len(check_limit) > 1):  # if warehouse's limit is provided
        warehouse_num, limit = args_list[2].split(" ")
        if (warehouse_num.isdigit()):
            if warehouse_num in warehouse_limit_dict:
                print("ERROR, CANNOT ADD DUPLICATE WAREHOUSE NUMBER")
            else:
                warehouse_limit_dict[warehouse_num] = int(limit)
        else:
            print("warehouse number should be a digit")

    else:                      # if warehouse's limit is not provided, set it as infinity
        warehouse_num = args_list[2]
        if (warehouse_num.isdigit()):
            if warehouse_num in warehouse_limit_dict:
                print("ERROR, CANNOT ADD DUPLICATE WAREHOUSE NUMBER")
            else:
                warehouse_limit_dict[warehouse_num] = inifinity
        else:
            print("warehouse number should be a digit")


# list all products
def handle_list_products(product_dict):
    for key, value in product_dict.items():
        print(value, key)


# list all warehouses
def handle_list_warehouses(warehouse_limit_dict):
    for key, value in warehouse_limit_dict.items():
        print(key)


# list detail in a warehouse
def handle_list_single_warehouse(warehouse_limit_dict, warehouse_product_dict, product_dict, args_list):
    if (len(args_list) < 3):
        print("please give specific warehouse number")
        return
    if(args_list[2].isdigit()):
        print("ITEM_NAME      ITEM_SKU        QTY")
        for ware_num, warehouse_limit_dict in warehouse_product_dict.items():
            for sku_key in warehouse_limit_dict.keys():
                quantity = warehouse_limit_dict[sku_key]
                print(product_dict[sku_key], sku_key, quantity)
    else:
        print("warehouse number should be integer number")


# handle all stock-related operation
def handle_all_stock(warehouse_product_dict, product_dict,
                     warehouse_limit_dict, args_list):
    if (args_list[0].upper() == "STOCK"):
        handle_stock(warehouse_product_dict, product_dict,
                     warehouse_limit_dict, args_list)
    elif (args_list[0].upper() == "UNSTOCK"):
        handle_unstock(warehouse_product_dict, product_dict,
                       warehouse_limit_dict, args_list)


# handle stock operation
def handle_stock(warehouse_product_dict, product_dict,
                 warehouse_limit_dict, args_list):
    sku = args_list[1]
    warehouse_num = args_list[2]
    quantity = int(args_list[3])
    try:
        limit = warehouse_limit_dict[warehouse_num]
    except KeyError:
        print("this warehouse does not exist")
        return
    if(warehouse_num not in warehouse_limit_dict):  # determine if this is a valid warehouse number
        print("Warehouse number is not valid")
        return
    if(sku not in product_dict):  # determine if this is a valid sku in product catalog
        print("SKU is not valid")
        return

    try:  # handle the initialized case, where this warehouse never stocked before
        sku_qty_dict = warehouse_product_dict[warehouse_num]
    except KeyError:
        sku_qty_dict = {}

    try:  # handle the initialized case, where this warehouse never stock this kind of product before
        current_quantity = sku_qty_dict[sku]
    except KeyError:
        sku_qty_dict[sku] = 0
        current_quantity = 0
    if(current_quantity+quantity > limit):  # if stock exceeds the limit
        print("Reach the limit, but still stock the maximum as we can for {limit} items".format(
            limit=limit))
        sku_qty_dict[sku] = limit
    else:
        sku_qty_dict[sku] += quantity
    warehouse_product_dict[warehouse_num] = sku_qty_dict


# handle unstock operation
def handle_unstock(warehouse_product_dict, product_dict,
                   warehouse_limit_dict, args_list):

    sku = args_list[1]
    warehouse_num = args_list[2]
    quantity = int(args_list[3])

    if(warehouse_num not in warehouse_limit_dict):  # determine if this is a valid warehouse number
        print("Warehouse number is not valid")
        return
    if(sku not in product_dict):  # determine if this is a valid sku in product catalog
        print("SKU is not valid")
        return

    try:  # handle the initialized case, where this warehouse never stocked before
        sku_qty_dict = warehouse_product_dict[warehouse_num]
    except KeyError:
        sku_qty_dict = {}

    try:  # handle the initialized case, where this warehouse never stock this kind of product before
        current_quantity = sku_qty_dict[sku]
    except KeyError:
        current_quantity = 0
    if(current_quantity-quantity < 0):  # if stock lower than 0
        print("Reach the limit of 0, give all the items")
        sku_qty_dict[sku] = 0
    else:
        sku_qty_dict[sku] -= quantity
    warehouse_product_dict[warehouse_num] = sku_qty_dict


def main():
    print("Welcome! Start your operations here :)")
    print("To exit, prompt 'exit' or ctrl+c")

    product_dict = {}  # store as sku and product as pair, sku:product_name
    warehouse_limit_dict = {}  # store warehouses number and their limitation

    # store the warehouse # and {sku,QTY} as pair, this is a dictionary inside dictionary
    warehouse_product_dict = {}
    # the pair looks like: {warehouse#:[sku,QTY]}
    f = open("log.txt", 'w')
    async_count = 0
    string_1 = None
    string_2 = None
    while True:
        input_arg = input("input here: ")
        if (async_count == 0):  # this block handles the async command_history
            string_1 = input_arg+'\n'
            async_count += 1
        elif(async_count == 1):
            string_2 = input_arg+'\n'
            task = handle_command_history(
                f, string_1, string_2)  # run an async task
            asyncio.run(task)
            async_count = 0
        if(input_arg.lower() == "exit"):
            f.close()
            sys.exit(0)
        args_list = input_arg.split(" ", 2)
        if(len(args_list) == 0):
            print("wrong argument, please input again")
            continue
        if(args_list[0].upper() == "ADD"):
            handle_all_add(product_dict, warehouse_limit_dict, args_list)
        elif(args_list[0].upper() == "LIST"):
            handle_all_list(product_dict, warehouse_limit_dict,
                            warehouse_product_dict, args_list)
        elif(args_list[0].upper() == "STOCK" or args_list[0].upper() == "UNSTOCK"):
            args_list = input_arg.split(" ")
            handle_all_stock(warehouse_product_dict, product_dict,
                             warehouse_limit_dict, args_list)


if __name__ == "__main__":
    main()
