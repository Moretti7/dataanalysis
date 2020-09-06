package com.filatov.utils

import com.filatov.ENGLISH_STEMMER

fun String.stemming(): String {
    ENGLISH_STEMMER.current = this
    ENGLISH_STEMMER.stem()
    return ENGLISH_STEMMER.current
}

fun String.removeStopWords(stopWords: Set<String>) = this.splitToSequence(" ")
    .filter { !stopWords.contains(it) }
    .joinToString(separator = " ")

fun String.stemmingForWords() = this.splitToSequence(" ")
    .map { it.stemming() }
    .joinToString(separator = " ")

fun List<String>.transformContent(stopWords: Set<String>) = this.map { it.transformContent(stopWords) }

fun String.transformContent(stopWords: Set<String>) = this.toLowerCase().removeStopWords(stopWords).stemmingForWords()

fun List<String>.splitStringsToWords() = this.asSequence()
    .flatMap { it.splitToSequence(" ") }
    .filter { it.isNotEmpty() }
    .toList()

fun String.splitStringsToWords() = this.splitToSequence(" ")
    .filter { it.isNotEmpty() }
    .joinToString(separator = " ")

