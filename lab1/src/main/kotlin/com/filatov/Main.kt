package com.filatov

import com.fasterxml.jackson.databind.ObjectMapper
import com.filatov.model.CsvRow
import com.filatov.model.MessageCategory
import com.filatov.utils.splitStringsToWords
import com.filatov.utils.transformContent
import snowball.ext.englishStemmer
import java.io.BufferedReader
import java.io.FileReader
import java.io.FileWriter
import java.nio.file.Files
import java.nio.file.Paths
import java.util.regex.Pattern


val PATTERN = Pattern.compile("""(?im)^(\w+),(.+)$""")
val MULTIPLE_SPACE_PATTERN = Regex("""\s{2,}""")
val VALID_CHAR_PATTERN = Pattern.compile("""[\p{Alpha}\s]""")
val ENGLISH_STEMMER = englishStemmer()
const val INPUT_DIRECTORY = "input"
const val OUTPUT_DIRECTORY = "output"

fun main() {
    val objectMapper = ObjectMapper()
    val stopWords = readStopWords("$INPUT_DIRECTORY/stopwords.txt")

    val list = BufferedReader(FileReader("$INPUT_DIRECTORY/sms-spam-corpus.csv")).readLines().filter {
        PATTERN.matcher(it).find()
    }.toMutableList()
    list.removeAt(0)

    val categoryToMessages = list.asSequence()
        .map { mapToModel(it) }
        .groupBy({ it.category }, { it.content })
        .mapValues { it.value.transformContent(stopWords) }

    val typeToWordWithCount = categoryToMessages
        .map { it.key to it.value.splitStringsToWords() }
        .associateBy({ it.first }, { mapToWordsCount(it.second) })

    objectMapper.writeValue(
        FileWriter("word_length_distribution.json"),
        categoryToMessages.mapValues { wordLengthCount(it.value.splitStringsToWords().toSet().map { it.length }) }
    )
    objectMapper.writeValue(
        FileWriter("message_length_distribution.json"),
        categoryToMessages.mapValues { wordLengthCount(it.value.toSet().map { it.length }) }
    )

    writeToFiles(typeToWordWithCount)

    val result: MutableMap<MessageCategory, Map<String, Int>> = mutableMapOf()
    for ((type, wordsWithQuantity) in typeToWordWithCount) {
        val mostFrequentWords = wordsWithQuantity.asSequence()
            .sortedByDescending { it.value }
            .take(20)
            .associate { it.key to it.value }
        result[type] = mostFrequentWords
    }
    objectMapper.writeValue(FileWriter("most_frequent_words.json"), result)
}

fun String.retainAlphaAndSpaces() = this.asSequence()
    .filter { VALID_CHAR_PATTERN.matcher(it.toString()).find() }
    .map { it.toString() }
    .joinToString(separator = "")
    .replace(MULTIPLE_SPACE_PATTERN, " ")

fun readStopWords(fileName: String) = FileReader(fileName).use {
    it.readLines().toSet()
}

fun mapToModel(line: String): CsvRow {
    val matcher = PATTERN.matcher(line)
    matcher.find()
    val type = matcher.group(1)
    val content = matcher.group(2).retainAlphaAndSpaces()
    return CsvRow(type, content)
}

fun createDirectoryIfNotExists(directory: String) {
    val path = Paths.get(directory)
    if (!Files.exists(path)) {
        Files.createDirectories(path)
    }
}

fun writeToFiles(map: Map<MessageCategory, Map<String, Int>>) {
    for ((type, wordToCount) in map) {
        createDirectoryIfNotExists(OUTPUT_DIRECTORY)
        FileWriter("$OUTPUT_DIRECTORY/$type.txt").use {
            val fileWriter = it
            wordToCount.entries.stream().sorted { o1, o2 -> o2.value - o1.value }.forEach {
                fileWriter.write("${it.key} = ${it.value}\n")
                fileWriter.flush()
            }
        }
    }
}

fun mapToWordsCount(words: List<String>) = words.asSequence().groupingBy { it }.eachCount()

fun wordLengthCount(lengths: List<Int>) = lengths.groupingBy { it }.eachCount()
