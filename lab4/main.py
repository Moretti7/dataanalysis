import re
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
from copy import deepcopy
import networkx as nx


class Page:
    def __init__(self, url: str, index: int):
        self.url = url
        self.index = index
        self.parent_pages = set()
        self.child_pages = set()

    def from_json(self, jsn):
        self.__dict__ = jsn

    def add_child_page(self, child_url):
        self.child_pages.add(child_url)

    def add_parent_pages(self, parent_urls):
        self.parent_pages = set(parent_urls)

    def __repr__(self):
        return f"Page(url={self.url}; index={self.index}; parent_pages={self.parent_pages}; child_pages={self.child_pages})"


class PageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Page):
            return obj.__dict__
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class PageDecoder(json.JSONDecoder):
    def default(self, obj):
        return Page("", 0).from_json(obj)


def map_page_to_vector(page: Page, pages: dict):
    """pages - page.index -> page dict"""
    vector = list()

    for i in range(max(pages.values(), key=lambda it: it.index).index + 1):
        child_pages_count = 0
        current_page = pages[i]
        if page.url in current_page.child_pages:
            child_pages_count = len(current_page.child_pages)
        vector.append(1 / child_pages_count if child_pages_count > 0 else 0)

    array = np.array(vector)
    # print(f"page = {page.url}, vector = {array}")
    return array


if __name__ == '__main__':
    page_url = 'https://stackoverflow.com'
    processed_pages = set()
    pages = dict()
    child_parent_page_urls = dict()
    pages_queue = list()
    pages_queue.append(page_url)
    index = 0

    while True:
        current_page_url = pages_queue.pop()
        print(f"Downloading {current_page_url}, index = {index}")
        current_page = Page(current_page_url, index)
        pages[current_page_url] = current_page
        page = requests.get(current_page_url)
        exclude_pattern = f'(href="{current_page_url}/?#.+?")'
        # parsing_result = re.findall(f'href="({page_url}/.*?)"', page.text, re.MULTILINE)
        parsing_result = re.findall(f'href="({current_page_url}/.*?)(?:\?.+)?"', page.text, re.MULTILINE)
        anchor_links = map(lambda it: it.group(1), re.finditer(exclude_pattern, page.text, re.MULTILINE))

        for link_on_page in parsing_result:
            if link_on_page not in anchor_links and \
                    link_on_page != current_page_url and \
                    not re.search(r'(\.png|\.jpeg|\.jpg|\.xml|\.js|\.css)', link_on_page):
                if link_on_page not in processed_pages:
                    pages_queue.append(link_on_page)
                    processed_pages.add(link_on_page)

                if child_parent_page_urls.get(link_on_page) is None:
                    child_parent_page_urls[link_on_page] = set()
                child_parent_page_urls[link_on_page].add(current_page_url)
                current_page.add_child_page(link_on_page)

        index = index + 1
        if len(pages_queue) == 0:
            break
    print("Finished loading pages")
    for page in pages.values():
        parent_url = child_parent_page_urls.get(page.url)
        if parent_url is not None:
            page.add_parent_pages(parent_url)

    index_to_page = dict({k: v for (k, v) in map(lambda it: (it.index, it), pages.values())})
    # print(index_to_page)

    with open('stackoverflow_2.json', 'w') as file:
        file.write(json.dumps(index_to_page, indent=4, sort_keys=True, cls=PageEncoder))

    # index_to_page = dict()
    # with open('stackoverflow.json', 'r') as file:
    #     parsed_json = json.load(file)
    #     for k, v in parsed_json.items():
    #         page = Page("", 0)
    #         page.from_json(v)
    #         index_to_page[int(k)] = page

    vectors = []
    # for page in pages.values():
    for page in index_to_page.values():
        vectors.append(map_page_to_vector(page, index_to_page))

    matrix = np.array(vectors)

    # for vector in matrix:
    #     print(vector)

    page_ranks = np.ones(len(index_to_page))
    e = 0.00001
    b = 0.85
    while True:
        previous_page_rank = page_ranks
        # page_ranks = b + (1 - b) * (page_ranks.dot(matrix))
        page_ranks = b + (1 - b) * (matrix.dot(page_ranks))
        if np.all((page_ranks - previous_page_rank) < e):
            break

    result = []
    for (k, v) in index_to_page.items():
        result.append((v, page_ranks[k]))
        # print(f"{v.url} - {page_ranks[k]}")

    for el in sorted(result, key=lambda it: it[1], reverse=True)[1:10]:
        print(f"{el[0].url} - {el[1]}")

    plt.figure(figsize=(10, 10))
    G = nx.from_numpy_matrix(np.array((
        matrix
    )))
    nx.draw(G)
    plt.show()
