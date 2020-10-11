import random
import re
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np


def read_file(filename):
    points = []
    with open(filename, 'r') as file:
        for line in file:
            parsing_result = re.search(r'\s*(\d+)\s*(\d+)', line)
            x = int(parsing_result.group(1))
            y = int(parsing_result.group(2))
            points.append((x, y))
    return points


def mean(points, key_extractor):
    values = []
    for point in points:
        values.append(key_extractor(point))
    return np.mean(values)


def recalculate_centers(centroid_to_points, original_points):
    current_centroid_to_points = centroid_to_points

    while True:
        changed_points = 0

        centroids = []
        for i in range(0, len(current_centroid_to_points)):
            mean_x = mean(current_centroid_to_points[i], lambda point: point[0])
            mean_y = mean(current_centroid_to_points[i], lambda point: point[1])
            print(f"(mean_x, mean_y) = {(mean_x, mean_y)}")
            centroids.append((mean_x, mean_y))

        last_centroid_to_points = current_centroid_to_points
        current_centroid_to_points = clusterize(original_points, centroids)

        for centroid in current_centroid_to_points.keys():
            if current_centroid_to_points[centroid] != last_centroid_to_points[centroid]:
                changed_points = changed_points + 1

        if changed_points == 0:
            break
    # print("FOUND")
    return current_centroid_to_points, centroids


def calculate_distance_to_centroid(point, centroid_x, centroid_y):
    return sqrt((centroid_x - point[0]) ** 2 + (centroid_y - point[1]) ** 2)


def clusterize(points, centroids):
    point_to_centroids = {}
    for point in points:
        point_to_centroids[point] = []
        for centroid in centroids:
            point_to_centroids[point].append(calculate_distance_to_centroid(point, centroid[0], centroid[1]))

    centroid_to_points = {}
    for i in range(0, len(centroids)):
        centroid_to_points[i] = []

    for point in points:
        closest_centroid = point_to_centroids[point].index(min(point_to_centroids[point]))
        centroid_to_points[closest_centroid].append(point)
    return centroid_to_points


def run_k_mean(points, number_of_centroids):
    # point to list of distance to each centroid
    point_to_centroids = {}
    centroid_to_point = {}
    centroids = []
    min_x = min(points, key=lambda t: t[0])[0]
    max_x = max(points, key=lambda t: t[0])[0]
    min_y = min(points, key=lambda t: t[1])[1]
    max_y = max(points, key=lambda t: t[1])[1]

    # print(f"min_x = {min_x}, max_x = {max_x}, min_y = {min_y} max_y = {max_y}")

    for point in points:
        point_to_centroids[point] = []

    for i in range(0, number_of_centroids):
        random_x = random.randint(min_x, max_x)
        random_y = random.randint(min_y, max_y)
        centroids.append((random_x, random_y))
        # print(f"random_x = {random_x}, random_y = {random_y}")
        centroid_to_point[i] = []

    centroid_to_points = clusterize(points, centroids)
    # print(f"centroid_to_points = {centroid_to_points}")
    return recalculate_centers(centroid_to_points, points)

def request_file_name():
    choice_table = {
        '1': lambda: 'points datasets/birch1.txt',
        '2': lambda: 'points datasets/birch1.txt',
        '3': lambda: 'points datasets/birch1.txt',
        '4': lambda: 'points datasets/s1.txt',
        '5': lambda: input("Enter your filename: ")
    }

    print("Choose file: ")
    print("1. points datasets/birch1.txt")
    print("2. points datasets/birch1.txt")
    print("3. points datasets/birch1.txt")
    print("4. points datasets/s1.txt")
    print("5. Enter another file name")
    choice = input("Choose: ")
    return choice_table[choice]()


if __name__ == '__main__':
    file_name = request_file_name()
    points = read_file(file_name)
    plt.scatter(*zip(*points))
    plt.show()

    # print(points)
    # print(*zip(*points))

    number_of_centroids = int(input("Enter number of centroids: "))
    centroid_to_points, centroids = run_k_mean(points, number_of_centroids)

    for centroid in centroid_to_points:
        centroids_points = centroid_to_points[centroid]

        plt.scatter(*zip(*centroids_points))

    plt.scatter(*zip(*centroids), color='black')

    plt.show()
