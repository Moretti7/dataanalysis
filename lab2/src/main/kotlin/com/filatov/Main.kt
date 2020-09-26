package com.filatov

import com.filatov.model.CsvRow
import com.filatov.model.MessageCategory.HAM
import com.filatov.model.MessageCategory.SPAM
import com.filatov.utils.retainAlphaAndSpaces
import com.filatov.utils.transformContent
import snowball.ext.englishStemmer
import java.io.BufferedReader
import java.io.FileReader
import java.math.BigDecimal
import java.math.MathContext
import java.util.*
import java.util.regex.Pattern


val PATTERN = Pattern.compile("""(?im)^(\w+),(.+)$""")
val MULTIPLE_SPACE_PATTERN = Regex("""\s{2,}""")
val VALID_CHAR_PATTERN = Pattern.compile("""[\p{Alpha}\s]""")
val ENGLISH_STEMMER = englishStemmer()
const val INPUT_DIRECTORY = "input"
const val OUTPUT_DIRECTORY = "output"

operator fun BigDecimal.div(other: BigDecimal) = this.divide(other, MathContext.DECIMAL128)

fun main() {
    val stopWords = readStopWords("$INPUT_DIRECTORY/stopwords.txt")

    val list = BufferedReader(FileReader("$INPUT_DIRECTORY/sms-spam-corpus.csv")).readLines().filter {
        PATTERN.matcher(it).find()
    }.toMutableList()
    list.removeAt(0)

    val categoryToMessages = list.asSequence()
        .map { mapToModel(it) }
        .groupBy({ it.category }, { it.content })
        .mapValues { it.value.transformContent(stopWords) }

    val totalMessageCount = BigDecimal(categoryToMessages.keys.map { categoryToMessages[it]!!.size }.reduce(Int::plus))
    val spamCount = BigDecimal(categoryToMessages[SPAM]!!.size)
    val hamCount = BigDecimal(categoryToMessages[HAM]!!.size)

    val spamProbability = spamCount / totalMessageCount
    val hamProbability = hamCount / totalMessageCount

    println("totalMessageCount = $totalMessageCount")
    println("spamCount = $spamCount")
    println("hamCount = $hamCount")
    println("spamProbability = $spamProbability")
    println("hamProbability = $hamProbability")

    val scanner = Scanner(System.`in`)
    while (true) {
        print("Enter the message: ")
        val transformedUserInput = scanner.nextLine().retainAlphaAndSpaces().transformContent(stopWords)
        println("transformed user input = $transformedUserInput")

        val userInputSpamProbability = transformedUserInput.splitToSequence(" ")
            .map { P(it, categoryToMessages[SPAM]!!, categoryToMessages[HAM]!!.size) }
            .fold(BigDecimal.ONE, BigDecimal::times) * spamProbability

        val userInputHamProbability = transformedUserInput.splitToSequence(" ")
            .map { P(it, categoryToMessages[HAM]!!, categoryToMessages[SPAM]!!.size) }
            .fold(BigDecimal.ONE, BigDecimal::times) * hamProbability

        println("\n\nuserInputSpamProbability\t=\t${userInputSpamProbability.toPlainString()}")
        println("userInputHamProbability\t\t=\t${userInputHamProbability.toPlainString()}")

        println(if(userInputSpamProbability > userInputHamProbability) "Message is SPAM" else "Message is HAM")
        println("\n")
    }
}

fun P(word: String, category: List<String>, otherSampleCount: Int): BigDecimal {
    val quantityOfWordInCategory = category.asSequence()
        .flatMap { it.splitToSequence(" ") }
        .filter { it == word }
        .count()

    return if (quantityOfWordInCategory == 0) {
        BigDecimal(1) / BigDecimal(category.size + otherSampleCount)
    } else {
        BigDecimal(quantityOfWordInCategory) / BigDecimal(category.size)
    }
}

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
