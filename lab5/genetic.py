from typing import List
import xlrd
from random import random
from time import time

class Person:
    def __init__(self, products: List[str]):
        self.products = products
        self.fitness_value = 0

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Person) and o.products == self.products

    def __hash__(self) -> int:
        return hash(self.products)

    def __lt__(self, other):
        return self.fitness_value < other.fitness_value

    def __gt__(self, other):
        return self.fitness_value > other.fitness_value

    def __repr__(self):
        return f'Person(products = {self.products}; fitness_value = {self.fitness_value})'


def get_population(data_set_name):
    sheet = xlrd.open_workbook(data_set_name).sheet_by_index(0)
    invoice_to_product = dict()
    population_to_return = list()
    for row in range(1, sheet.nrows):
        invoice = str(sheet.cell_value(row, 0))
        product_id = str(sheet.cell_value(row, 1))
        if invoice in invoice_to_product:
            invoice_to_product[invoice].append(product_id)
        else:
            invoice_to_product[invoice] = [product_id]
    for k, v in invoice_to_product.items():
        # if len(v) > 3:
        if len(v) == 4:
            population_to_return.append(Person(v))
    return population_to_return, list(invoice_to_product.values())


def compute_fitness_values(person_p, products_from_file_p):
    person_products = person_p.products
    fitness_value = 0
    for el in products_from_file_p:
        matched_products_count = 0
        for el1 in person_products:
            if el1 in el:
                matched_products_count += 1
        if matched_products_count == len(person_products):
            fitness_value += 1
    person_p.fitness_value = fitness_value


def get_new_persons_using_tournament(population):
    first_person_index = int(random() * len(population))
    second_person_index = int(random() * len(population))
    third_person_index = int(random() * len(population))
    fourth_person_index = int(random() * len(population))
    selected_indexes = [first_person_index]
    while second_person_index in selected_indexes:
        second_person_index = int(random() * len(population))
    selected_indexes.append(second_person_index)
    while third_person_index in selected_indexes:
        third_person_index = int(random() * len(population))
    selected_indexes.append(third_person_index)
    while fourth_person_index == first_person_index:
        fourth_person_index = int(random() * len(population))

    first_person = population[first_person_index]
    second_person = population[second_person_index]
    third_person = population[third_person_index]
    fourth_person = population[fourth_person_index]

    persons_to_return = [first_person if first_person > second_person else second_person,
                         third_person if third_person > fourth_person else fourth_person]
    return persons_to_return


def create_new_persons(first_parent_p: Person, second_parent_p: Person):
    first_person_to_return = Person([*first_parent_p.products[0:2], *second_parent_p.products[2:]])
    second_person_to_return = Person([*first_parent_p.products[2:], *second_parent_p.products[:2]])
    # min_length = len(first_parent_p.products) if len(first_parent_p.products) < len(second_parent_p.products) else len(second_parent_p.products)
    # index_of_genome_division = int(random() * min_length)
    # first_person_to_return = Person([*first_parent_p.products[:index_of_genome_division], *second_parent_p.products[index_of_genome_division:]])
    # second_person_to_return = Person([*first_parent_p.products[index_of_genome_division:], *second_parent_p.products[:index_of_genome_division]])
    return first_person_to_return, second_person_to_return


def insert_into_population(parents, children, population_p):
    for child in children:
        for parent in parents:
            if child > parent:
                if parent in population_p:
                    population_p.remove(parent)
                population_p.append(child)


def mutate(population_p, products_from_file_p):
    for el in population_p:
        if random() < 0.01:
            while True:
                random_products_index = int(random() * len(products_from_file_p))
                random_product_index = int(random() * len(products_from_file_p[random_products_index]))
                random_product = products_from_file_p[random_products_index][random_product_index]
                if random_product not in el.products:
                    random_genome = int(random() * len(el.products))
                    el.products[random_genome] = random_product
                else:
                    continue
                break




if __name__ == '__main__':
    # number_of_generations = int(input("Введите число эпох: "))
    number_of_generations = 4
    # population, products_from_file = get_population('Online Retail Mini.xlsx') # contains only one person with 4 products
    population, products_from_file = get_population('Online Retail.xlsx')
    for person in population:
        compute_fitness_values(person, products_from_file)
        # print(person)
    persons_count = len(population)
    print(f'population count = {persons_count}')
    input()
    start_time = time()
    for generation in range(number_of_generations):
        print(f'Поколение №{generation + 1}')
        for k in range(persons_count):
            print(f'iteration № {k + 1}')
            first_parent, second_parent = get_new_persons_using_tournament(population)
            first_new_person, second_new_person = create_new_persons(first_parent, second_parent)
            compute_fitness_values(first_new_person, products_from_file)
            compute_fitness_values(second_new_person, products_from_file)
            insert_into_population([first_parent, second_parent], [first_new_person, second_new_person], population)
            mutate(population, products_from_file)
    end_time = time()
    population.sort(key=lambda it: it.fitness_value)
    for person in population:
        print(person)
    print(f'elapsed time = {end_time - start_time}')