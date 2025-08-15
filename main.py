"""This app makes suggestions for the next word to try while playing WORDLE."""

# TODO: make GUI-based version of app
# TODO: allow user to mark words as good/bad (e.g. acceptable to MS WORD or not)
# fix bug when one letter is found in the correct position, and another position contains the same letter

# CONSTANTS (almost, some are setup values that can be overridden by setup file entries
SETUP_FILENAME = "setup.txt"
WORDLE_LENGTH = 5
PREVIOUS_WORDLE_FILENAME = "Previous WORDLEs.txt"
WORDLE_FILENAME = "WORDLEs.txt"
WORD_FILENAME = "Scrabble Words.txt"
LINE_LENGTH = 80
RIGHT_RIGHT = "."
RIGHT_WRONG = "V"
WRONG_WRONG = " "
CANCEL_WORD = "-"
RIGHT_WORD = "+"
READ_FILE = "r"
WRITE_FILE = "w"
ALPHABET = "abcdefghijklmnopqrstuvwxyz".upper()
LETTER_MULTIPLIER = 10
FIRST_MULTIPLIER = 20
LAST_MULTIPLIER = 15
RECOMMENDED_WORDS = 20
WORD_LIST_INDENT = "    "
COMMA = ","


def apply_one_setup(setup, name, def_value) -> str:
    """Find a name/value pair in the setup object and return the value as a string."""
    name = name.upper()
    return setup[name.upper()] if name in setup else def_value


def apply_one_setup_int(setup, name, def_value) -> int:
    """Get an integer value from the setup dictionary or use the default value, if setup value is an invalid int."""
    value = apply_one_setup(setup, name, def_value)
    try:
        return int(value)
    except ValueError:
        return def_value


def apply_setup_values(setup) -> None:
    """Set select GLOBAL values from name/value pairs in the setup dictionary, or keep default values."""
    global PREVIOUS_WORDLE_FILENAME
    global WORDLE_FILENAME
    global WORD_FILENAME
    global LINE_LENGTH
    global LETTER_MULTIPLIER
    global FIRST_MULTIPLIER
    global LAST_MULTIPLIER

    PREVIOUS_WORDLE_FILENAME = apply_one_setup(setup, "Previous", PREVIOUS_WORDLE_FILENAME)
    WORDLE_FILENAME = apply_one_setup(setup, "Current", WORDLE_FILENAME)
    WORD_FILENAME = apply_one_setup(setup, "Vocabulary", WORD_FILENAME)
    LINE_LENGTH = apply_one_setup_int(setup, "Line length", LINE_LENGTH)
    LETTER_MULTIPLIER = apply_one_setup_int(setup, "Letter multiplier", LETTER_MULTIPLIER)
    FIRST_MULTIPLIER = apply_one_setup_int(setup, "First multiplier", FIRST_MULTIPLIER)
    LAST_MULTIPLIER = apply_one_setup_int(setup, "Last multiplier", LAST_MULTIPLIER)


def read_setup(setup_filename):
    """Read the setup file and parse it into a setup dictionary."""
    # start with an empty setup dictionary
    setup = {}
    try:
        # open the setup file and process each line
        with open(setup_filename, READ_FILE) as f:
            for line in f:
                line = line.strip()
                # ignore blank lines and comment lines (starting with #)
                if len(line) == 0 or line[0] == "#":
                    continue
                # cut off the end of any lines that have a '#' in them (trailing comment)
                if '#' in line:
                    line = line.split("#", 1)[0]
                # setup lines are in the form 'name = value'
                # enter valid setup pairs in the setup dictionary, report and discard any other lines
                if "=" in line:
                    entry = line.split("=", 1)
                    entry[0] = entry[0].strip().upper()
                    entry[1] = entry[1].strip()
                    setup[entry[0]] = entry[1]
                else:
                    print(f"Invalid line in setup file: '{line}'")
    except FileNotFoundError:
        # no setup file
        print(f"Setup file was not found in '{setup_filename}, using defaults.'")
        pass

    return setup


def read_WORDLE_list(filename, old_filename) -> tuple:
    """Read history of WORDLE guesses and successful words-list of previous WORDLE words for hinting analysis."""
    wordles_all = []
    # if there is a current WORDLE list, use that
    try:
        with open(filename, READ_FILE) as f1:
            wordles_all = [line.upper().split() for line in f1]
    except FileNotFoundError:
        # couldn't find the current WORDLE file, look for the old one
        try:
            with open(old_filename, READ_FILE) as f2:
                wordles_all = [line.split("—", 1)[1].replace("*", " ").upper().split() for line in f2]
        except FileNotFoundError:
            # couldn't find either a current or old WORDLE list file, carry on without
            pass
    # create the successful WORDLE list from the WORDLE attempts list
    wordles = [entry[-1] for entry in wordles_all]
    return wordles, wordles_all


def save_WORDLE_file(filename, rounds):
    """Write all the previous rounds of WORDLE, plus the current round, to the WORDLE file."""
    with open(filename, WRITE_FILE) as f:
        for a_round in rounds:
            f.write(f"{' '.join(a_round)}\n")


def read_word_list(filename, word_length=0):
    """Read the list of possible words, but filter it for only the words of the right length."""
    with open(filename, READ_FILE) as f:
        word_list = [word.strip().upper() for word in f if word_length == 0 or len(word.strip()) == word_length]
    return word_list


def get_guess(word_list, WORDLE_list) -> str:
    """Ask for the next word guess, allow user to change mind if word is not in vocab or previously used."""
    while True:
        # get the word for this guess and condition it (remove white space and make uppercase)
        print()
        guess = input("Enter your guess word: ").strip().upper()
        print()
        # is the 'word' empty?
        if guess == "":
            print("Nothing entered, please try again")
            continue
        # is the 'word' all letters?
        if not guess.isalpha():
            print("Invalid guess, must be all alpha characters")
            continue
        # is the word the right length?
        if len(guess) != WORDLE_LENGTH:
            print(f"Invalid guess, must be {WORDLE_LENGTH} letters in length")
            continue
        # is the word in the valid vocabulary list?
        if not (guess in word_list):
            answer = input(f"Your guess, {guess}, is not in the vocabulary list, are you sure you want to use it? ").\
                strip().upper()
            if len(answer) < 1 or answer[0] != "Y":
                continue
        # has this word already been a previous WORDLE word?
        if guess in WORDLE_list:
            answer = input(f"Your guess, {guess}, has already been used as a WORDLE word, are you sure you want to use it? ").\
                strip().upper()
            if len(answer) < 1 or answer[0] != "Y":
                continue
        return guess


def get_result(guess):
    """Ask the user for a string that represents which letters are right, wrong, misplaced, etc."""
    good_result = False
    result = ""
    while not good_result:
        good_result = True
        print()
        if WRONG_WRONG == " ":
            print("Enter a space under any letter that is wrong,")
        else:
            print(f"Enter a '{WRONG_WRONG}' under any letter that is wrong,")
        print(f"a '{RIGHT_WRONG}' under any correct letter in the wrong place,")
        print(f"and a '{RIGHT_RIGHT}' under any correct letter in the right place.")
        print(f"Enter a '{CANCEL_WORD}' to switch to a different word.")
        print(f"Enter a '{RIGHT_WORD}' if this was the correct word.")
        print(guess)
        result = input().upper()
        if len(result) > WORDLE_LENGTH:
            result = result[:5]
        while len(result) < WORDLE_LENGTH:
            result += WRONG_WRONG
        for c in result:
            if c != WRONG_WRONG and c != RIGHT_WRONG and c != RIGHT_RIGHT and c != CANCEL_WORD and c != RIGHT_WORD:
                print("Result string is invalid, please re-enter")
                good_result = False
                break
    return result


def reduce_words(possible_words, guess, result, can, at_least, definite):
    """Reduce the list of remaining possible words based on the latest (and previous) guesses and results."""
    # adjust the at_least dictionary based on the results of the latest guess
    # count the number of each letter in the word (to handle doubles and triples)
    full_letter_count = {}
    wrong_letter_count = {}
    for i, c in enumerate(result):
        lett = guess[i]
        if c == RIGHT_RIGHT or c == RIGHT_WRONG:
            if lett not in full_letter_count:
                full_letter_count[lett] = 1
            else:
                full_letter_count[lett] += 1
        if c == RIGHT_WRONG:
            if lett not in wrong_letter_count:
                wrong_letter_count[lett] = 1
            else:
                wrong_letter_count[lett] += 1

    # now transfer this knowledge to the at_least dictionary pattern
    for lett, value in full_letter_count.items():
        if lett not in at_least:
            at_least[lett] = value
        else:
            at_least[lett] = max(at_least[lett], value)

    # look at each of the results for the letter positions in order to set the "can have" and "is" patterns
    for i, c in enumerate(result):
        # make the letter easily available
        lett = guess[i]

        # right letter in the right place
        # set the clues variables: _can have_ this letter, _is_ this letter
        if c == RIGHT_RIGHT:
            can[i] = lett
            definite[i] = lett

        # right letter in the wrong place
        # set the clues variable: _can NOT have_ this letter here
        elif c == RIGHT_WRONG:
            # this letter cannot be in this position
            can[i] = can[i].replace(lett, "")

    # look at each of the wrong_wrong results for the letter positions in order to indicate where letters cannot go
    for i, c in enumerate(result):
        # make the letter easily available
        lett = guess[i]

        # wrong letter (and wrong place, of course)
        # adjust the clue variable: _can NOT have_ this letter anywhere (except definites)
        if c == WRONG_WRONG:
            if lett not in wrong_letter_count:
                # a wrong letter that is not in the wrong_letter_count means this letter does not belong in any slot that is not definite
                for j, cans in enumerate(can):
                    if definite[j] == "":
                        can[j] = cans.replace(lett, "")

            else:
                # this letter is in the wrong_letter_count, so it goes somewhere in the word, but not here
                can[j] = can[j].replace(lett, "")

    # now filter out all the words that don't fit the patterns
    new_word_list = []
    for word in possible_words:
        good_word = True

        # is each of the definite letters in the word in the right place?
        for j, c in enumerate(word):
            if definite[j] != "" and c != definite[j]:
                good_word = False
                break

        # is each letter in the list of possibles for that position?
        # note that for definites, the only possible letter is the definite letter
        if good_word:
            for j, c in enumerate(word):
                if can[j].find(c) < 0:
                    good_word = False
                    break

        # does the word contain all required letters?
        # note: definite letters are not counted in the required letters
        if good_word:
            # first, count all the letters in this word
            full_letter_count = {}
            for lett in word:
                if lett not in full_letter_count:
                    full_letter_count[lett] = 1
                else:
                    full_letter_count[lett] = full_letter_count[lett] + 1

            # now see if the word contains at least the number of each letter required so far
            for lett, count in at_least.items():
                if lett not in full_letter_count or full_letter_count[lett] < count:
                    good_word = False
                    break

            # if this word passed all tests, add it to the new word list
            if good_word:
                new_word_list.append(word)

    return new_word_list


def show_words(words, commas=True, word_len=WORDLE_LENGTH, lowercase=False, upper_limit=-1, indent=True):
    """Show a list of words.
        list may be comma separated: commas=True (default)
        list may be shown in lowercase (except final word): lowercase=False (default)
        an upper limit on number of words shown: upper_limit=# (default no limit)
        list may be indented: indent=True (default)"""
    # need to know how many words there are to show to treat the last word differently
    word_count = len(words)
    # calculate how many words to show on each line
    words_per_line = LINE_LENGTH // (word_len + 2)
    # keep track of the number of words printed on each line
    words_on_line = 0
    # select indentation
    indentation = WORD_LIST_INDENT if indent else ""
    # select separator
    separator = ({COMMA} if commas else "") + " "
    # print each word in the list, possibly separated by commas, possibly lower case except last word
    print(indentation, end="")
    for i, word in enumerate(words):
        if (upper_limit >= 0) and (i >= upper_limit):
            print()
            break
        if i < (word_count - 1):
            # should all but last word be printed in lowercase?
            if lowercase:
                word = word.lower()
            print(f"{word}{separator}", end="")
            # if maximum words have been printed on this line, start a new line
            words_on_line += 1
            if words_on_line >= words_per_line:
                words_on_line = 0
                print(f"\n{indentation}", end="")
        else:
            # last word is always printed in uppercase without a trailing comma
            print(f"{word}")


def split_possibles(possibles, WORDLE_list):
    """Split a list of possible words into two lists -- words that have been used before and those that haven't."""
    unused_word_list = []
    previously_used_word_list = []
    for word in possibles:
        previously_used_word_list.append(word) if word in WORDLE_list else unused_word_list.append(word)
    return unused_word_list, previously_used_word_list


def score_possibles(possibles, WORDLE_list):
    """Analyze the previous rounds of WORDLE to make recommendations for the 'most likely' words."""
    # analyze the previous WORDLES
    all_letter_freq = [0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    first_letter_freq = [0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    last_letter_freq = [0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    # count the occurrences of each letter and a total count of letters
    total_letters = 0
    total_words = len(WORDLE_list)
    for word in WORDLE_list:
        word = word.upper()
        first_letter_freq[ALPHABET.find(word[0])] += 1
        last_letter_freq[ALPHABET.find(word[-1])] += 1
        for letter in word:
            all_letter_freq[ALPHABET.find(letter)] += 1
            total_letters += 1
    # calculate the probability of each letter and each first and last letter
    for i in range(len(all_letter_freq)):
        all_letter_freq[i] /= total_letters
        first_letter_freq[i] /= total_words
        last_letter_freq[i] /= total_words

    # calculate a probability score for each word and build a list of tuples
    scored_words = []
    for word in possibles:
        # raise the score for having more common first and last letters
        score = first_letter_freq[ALPHABET.find(word[0])] * FIRST_MULTIPLIER + \
                last_letter_freq[ALPHABET.find(word[-1])] * LAST_MULTIPLIER
        # add scores for frequencies of all letters
        for letter in word.upper():
            score += all_letter_freq[ALPHABET.find(letter)] * LETTER_MULTIPLIER
        # lower the score for possible plurals or past-tense verbs
        if word.endswith("ED") or word.endswith("ES") or word.endswith("S"):
            score -= 1
        # lower the score for duplicate letters
        for letter in word:
            if word.count(letter) > 1:
                score -= 0.5
        scored_words.append((word, score))
    scored_words.sort(reverse=True, key=lambda w: w[1])
    return scored_words


def show_scored_words(scored_words):
    """Print out a short list of the highest scoring WORDLE word suggestions."""
    top_words = min(RECOMMENDED_WORDS, len(scored_words))
    if top_words > 0:
        if top_words == 1:
            print("There is only one word left in the recommended word list:")
        else:
            print(f"Top {top_words} recommended words:")
        show_words(list(w[0] for w in scored_words), commas=False, upper_limit=top_words)
    else:
        print("There are no words left in the recommended word list, sorry...you're on your own!")


def process_guesses(wordlist, WORDLE_list):
    """Process WORDLE word guesses until a full round is complete."""
    guess_list = []
    can = []
    at_least = {}
    definite = []
    for _ in range(WORDLE_LENGTH):
        can.append(ALPHABET)
        definite.append("")
    possibles = wordlist.copy()
    while True:
        while True:
            guess = get_guess(wordlist, WORDLE_list)
            print("Now, enter your guess in WORDLE and indicate the results below:")
            result = get_result(guess)
            if CANCEL_WORD not in result:
                break
            print("Cancelling most recent guess")
        guess_list.append(guess)
        # if we have found the right word, terminate processing guesses
        if result == RIGHT_RIGHT * WORDLE_LENGTH or RIGHT_WORD in result:
            break
        # cut out all the words that don't match our patterns
        possibles = reduce_words(possibles, guess, result, can, at_least, definite)
        # split the possibles list into non-used and previously-used words
        new_possibles, old_possibles = split_possibles(possibles, WORDLE_list)
        # calculate a probability of each word being correct (algorithm in progress)
        scored_words = score_possibles(new_possibles, WORDLE_list)
        # print some of the highest scoring words
        show_scored_words(scored_words)
        # print the list of words that is still viable
        print(f"Unused possible words from vocabulary list ({len(new_possibles):,}):")
        show_words(new_possibles, commas=False)
        if len(old_possibles) > 0:
            print(f"Previously used possible words from vocabulary list ({len(old_possibles):,}):")
            show_words(old_possibles, commas=False)
    print()
    print(f"Success! You got it in {len(guess_list)}. The guess sequence is:")
    show_words(guess_list, commas=False, lowercase=True, indent=True)
    return guess_list


def show_stats(rounds):
    """Show the statistics and bar chart for all the WORDLE games the user has played."""
    tries_table = [0 for _ in range(12)]
    total_rounds = len(rounds)
    for a_round in rounds:
        tries = len(a_round) - 1
        if tries < len(tries_table):
            tries_table[tries] += 1
    total_tries = 0
    for i in range(len(tries_table)):
        total_tries += (i+1) * tries_table[i]
    print(f"Win tries chart (mean: {total_tries / total_rounds:.3} after {total_rounds} games):")
    m = max(tries_table)
    for i, v in enumerate(tries_table):
        print(f"{i+1:2} ({v:3}) {'=' * int(v / m * LINE_LENGTH)}")


def main(setup_filename):
    """main method for WORDLE word guessing program."""
    # read the setup file for initial values
    setup = read_setup(setup_filename)
    apply_setup_values(setup)

    # read the list of possible WORDLE words (5-letter words only)
    word_list = read_word_list(WORD_FILENAME, WORDLE_LENGTH)
    print(f"5-letter vocabulary words loaded: {len(word_list):,} words")

    # read the list of previous WORDLE words (also the list of guesses for each round)
    WORDLE_list, WORDLE_rounds = read_WORDLE_list(WORDLE_FILENAME, PREVIOUS_WORDLE_FILENAME)
    print(f"Previous WORDLE words loaded: {len(WORDLE_list):,} words")

    another = "Y"
    while another == "Y":
        # show current WORDLE guess statistics before we start this round
        show_stats(WORDLE_rounds)

        # process player's WORDLE guesses and make suggestions
        guess_list = process_guesses(word_list, WORDLE_list)

        # see if player is done and if they want this round's results saved
        while True:
            print()
            another = input("Play another round? Y/N/(X to exit without saving this round): ").upper().strip()
            if (len(another) == 1) and (another in "YNX"):
                break
            print(f"'{another}' is not a valid action")

        if another != "X":
            # save round results to WORDLE file here
            WORDLE_rounds.append(guess_list)
            WORDLE_list.append(guess_list[-1])
            save_WORDLE_file(WORDLE_FILENAME, WORDLE_rounds)
        else:
            print("Round results not saved")

    # show new stats at end of play
    show_stats(WORDLE_rounds)

    print()
    print("All done...thanks for playing")


# start the main app
if __name__ == '__main__':
    main(SETUP_FILENAME)
