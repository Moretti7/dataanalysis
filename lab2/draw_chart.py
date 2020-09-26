import json

import matplotlib.pyplot as plt

OUTPUT_DIRECTORY = 'output'

def create_distribution_chart(data, file_name):
    for category in data:
        words_length = []
        quantities = []
        for word_length, quantity in data[category].items():
            words_length.append(int(word_length))
            quantities.append(quantity)

        words_length, quantities = zip(*sorted(zip(words_length, quantities)))

        fig, ax = plt.subplots(figsize=(20, 10))
        ax.plot(words_length, quantities)

        ax.set(xlabel=f'word length\nAverage length: {sum(words_length) / len(words_length)}', ylabel='word quantity')
        # ax.grid()

        fig.savefig(f"{OUTPUT_DIRECTORY}/{category}_{file_name}.png")
        # plt.show()


def create_frequent_words_chart(data, file_name):
    for category in data:
        words = []
        quantities = []
        for word, quantity in data[category].items():
            words.append(word)
            quantities.append(quantity)

        # words, quantities = zip(*sorted(zip(words, quantities)))
        quantities, words = zip(*sorted(zip(quantities, words)))

        fig, ax = plt.subplots(figsize=(20, 10))
        ax.plot(words, quantities)

        ax.set(xlabel='word', ylabel='frequency')
        # ax.grid()

        fig.savefig(f"{OUTPUT_DIRECTORY}/{category}_{file_name}.png")
        # plt.show()


def word_length_distribution():
    with open('word_length_distribution.json') as json_file:
        data = json.load(json_file)

    create_distribution_chart(data, 'word_length_quantity')


def message_length_distribution():
    with open('message_length_distribution.json') as json_file:
        data = json.load(json_file)

    create_distribution_chart(data, 'message_length_quantity')


if __name__ == '__main__':
    word_length_distribution()
    message_length_distribution()
    with open('most_frequent_words.json') as json_file:
        data = json.load(json_file)
        create_frequent_words_chart(data, 'word_frequency')
