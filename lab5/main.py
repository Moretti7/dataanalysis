import xlrd
import itertools
import time

from typing import List, Set


def get_products_to_exclude(all_products: List[list], combinations: Set[tuple], support: int):
    combinations_count = dict()

    for products in all_products:
        products_set = set(products)
        for combination in combinations:
            if len(set(combination).intersection(products_set)) == len(combination):
                if combination in combinations_count:
                    combinations_count[combination] += 1
                else:
                    combinations_count[combination] = 1
    result = set()
    for k, v in combinations_count.items():
        if v < support:
            result.add(k)
    return result

if __name__ == '__main__':
    sheet = xlrd.open_workbook('Online Retail Mini.xlsx').sheet_by_index(0)
    invoice_to_product = dict()
    for row in range(1, sheet.nrows):
        invoice = sheet.cell_value(row, 0)
        product_id = sheet.cell_value(row, 1)
        if invoice in invoice_to_product:
            invoice_to_product[invoice].append(product_id)
        else:
            invoice_to_product[invoice] = [product_id]

    # print(invoice_to_products)

    support = int(input("На даном датасете максимальное количество комбинаций которые повторяются состоит из 6 "
                        "елементов\nEnter min support: "))
    # support = 6
    # invoice_to_product = {
    #     100: ['a', 'b', 'c'],
    #     200: ['b', 'd'],
    #     300: ['b', 'a', 'd', 'c'],
    #     400: ['e', 'd'],
    #     500: ['a', 'b', 'c', 'd'],
    #     600: ['f']
    # }

    products = set()
    result = set()
    for v in invoice_to_product.values():
        products = products.union(v)

    # 1 составить комбинации из N елементов
    # 2 посчитать количество вхождений
    # 3 отсеить те которых меньше чем support
    start = time.time()
    result = set()
    for i in range(1, support + 1):
    # for i in range(1, 2):
        combinations = set(itertools.combinations(products, i))
        products_to_exclude = get_products_to_exclude(invoice_to_product.values(), combinations, support)

        for val in products_to_exclude:
            combinations.discard(val)
        products.clear()
        result.clear()

        for el in combinations:
            result.add(el)
            for el1 in el:
                products.add(el1)

    end = time.time()

    print(f"elapsed time = {end - start}")
    for el in result:
        print(el)