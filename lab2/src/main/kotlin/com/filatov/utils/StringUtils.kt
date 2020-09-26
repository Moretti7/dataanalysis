package com.filatov.utils

import com.filatov.ENGLISH_STEMMER
import com.filatov.MULTIPLE_SPACE_PATTERN
import com.filatov.VALID_CHAR_PATTERN

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

fun String.retainAlphaAndSpaces() = this.asSequence()
    .filter { VALID_CHAR_PATTERN.matcher(it.toString()).find() }
    .map { it.toString() }
    .joinToString(separator = "")
    .replace(MULTIPLE_SPACE_PATTERN, " ")
