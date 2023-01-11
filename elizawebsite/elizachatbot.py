# Importing the required libraries
import re
import random
from string import punctuation
import json
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from pathlib import Path
import os

nltk.download('averaged_perceptron_tagger', quiet=True)

# Defining required global variables
global RANK
global KEY_STACK
global REPLIES


# This function is used to load the pre-defined rules Eliza uses to spot keywords along with decomposition
# rules(regular expression patterns) and rearrangement rules (replies).
def load_dict():
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    RULES_DIR = os.path.join(BASE_DIR, 'elizawebsite')
    RULES_DIR = os.path.join(RULES_DIR, 'chatbot_rules.json')

    with open(RULES_DIR, "r") as chatbot_rules_json:
        rules_dict = json.load(chatbot_rules_json)
    return rules_dict


# Loading our pre-defined keyword dictionary
null = 'null'
chatbot_rules = load_dict()


# Function to remove punctuations and convert multiple space to single space
def clean_text(text):
    text = re.sub(rf"[{punctuation}]", "", text)
    text = re.sub(r"\W+", " ", text)
    return text


# It takes keyword as input and gets rank for the keyword from the pre-defined dictionary.Based on the rank it will
# arrange the keyword in a list. If the rank is higher, the keyword is palced in the begining of the list.
def get_rank(token):
    global RANK
    global KEY_STACK

    if chatbot_rules.get(token) is not None:
        rank_ = chatbot_rules.get(token).get('RANK')
        if rank_ is None:
            rank_ = 0
        if RANK > int(rank_):
            KEY_STACK = KEY_STACK + [token]
        else:
            KEY_STACK = [token] + KEY_STACK
            RANK = int(rank_)
    else:
        return "TOKEN_NOT_FOUND"


# Takes token and user input , applies transformation (pronoun, 'AM to ARE' or other similar conversion) ,
# then apply decomposition and rearrangement rules for the keyword and returns Eliza's response.
def get_reply(token, text):
    global REPLIES
    token_transformation_dict = dict()
    transformation_flag = False
    decoposition_rule = list(chatbot_rules.get(token).keys())

    if decoposition_rule is None:
        return "DECOMPOSITION_RULE_NOT_FOUND"

    if chatbot_rules.get(token).get("TRANSFORMATION") not in [None, 'null']:
        transformation_flag = True

    words = word_tokenize(text)
    for i in range(0, len(words)):
        if words[i] == token and transformation_flag:
            words[i] = chatbot_rules.get(token).get("TRANSFORMATION")
            continue
        if token == "I" and words[i] == "YOU":
            words[i] = pronoun_transform(words[i])
            continue
        if token == "YOU" and words[i] == "I":
            words[i] = pronoun_transform(words[i])
            continue
        if words[i] != token:
            pronoun = pronoun_transform(words[i])

            if pronoun is not None:
                words[i] = pronoun
            else:
                transformed_token = token_transform(words[i])
                if transformed_token is not None:
                    token_transformation_dict[transformed_token] = words[i]
                    words[i] = transformed_token
    text = " ".join(words)

    for rule in decoposition_rule:

        if rule == 'RANK' or rule == 'TRANSFORMATION':
            continue

        rule_t = rule.split()
        pattern = "(" + rule_t[0] + ")"
        for i in range(0, len(rule_t) - 1):
            if rule_t[i] != '0' and rule_t[i + 1] != 0:
                pattern = pattern + " " + "(" + rule_t[i + 1] + ")"
            else:
                pattern = pattern + "(" + rule_t[i + 1] + ")"

        pattern = pattern.replace('0', r'[a-zA-Z0-9 _]*').strip()
        # print(pattern, text)
        match = re.match(pattern, " " + text.upper() + " ")
        print(pattern,text, token)
        if match is None:
            continue
        reply = chatbot_rules.get(token).get(rule)[0]
        reply = reply.capitalize()

        if "=" in reply:
            reply = get_reply(reply.replace("=", "").strip(), text)
            return reply

        if reply.upper() == 'NEWKEY':
            return "NEXT_KEY"

        if match is not None:
            match = match.groups()
            random.shuffle(chatbot_rules.get(token).get(rule))
            for word in reply.split():
                if word.strip().isnumeric():
                    replacement = match[int(word) - 1]
                    for key in token_transformation_dict.keys():
                        replacement = replacement.replace(key, token_transformation_dict[key])
                    replacement = replacement.split()
                    for i in range(0, len(replacement)):
                        if replacement[i] == 'I':
                            replacement[i] = 'ME'
                            continue
                        if replacement[i] == 'ME':
                            replacement[i] = 'YOU'
                    replacement = ' '.join(replacement)
                    reply = reply.replace(word.strip(), replacement.lower())

            if rule == '0':
                REPLIES.append(reply)
            else:
                REPLIES = [reply]+REPLIES
                return "DONT_SEARCH_FURTHER"
            if token in ['SORRY', 'DREAM', 'DREAMT']:
                REPLIES = [reply]+REPLIES
                print("search stopped!")
                return "DONT_SEARCH_FURTHER"
            return reply
        else:
            reply = "MATCH_NOT_FOUND"


# In[8]: This function contains rules for pronoun and other transformation
def pronoun_transform(token):
    pronoun_dict = dict()
    pronoun_dict["I"] = "YOU"
    pronoun_dict["YOUR"] = "MY"
    pronoun_dict["MY"] = "YOUR"
    pronoun_dict["YOU"] = "I"
    pronoun_dict["AM"] = "ARE"
    pronoun_dict["ARE"] = "AM"

    # Make a list of it
    if pronoun_dict.get(token) is not None:
        return pronoun_dict.get(token)
    return None

def token_transform(token):
    token_dict = dict()
    token_dict["MOTHER"] = "FAMILY"
    token_dict["FATHER"] = "FAMILY"
    token_dict["MOM"] = "FAMILY"
    token_dict["DAD"] = "FAMILY"
    token_dict["WIFE"] = "FAMILY"
    token_dict["BROTHER"] = "FAMILY"
    token_dict["CHILDREN"] = "FAMILY"
    token_dict["SISTER"] = "FAMILY"
    token_dict["FEEL"] = "BELIEF"
    token_dict["THINK"] = "BELIEF"
    token_dict["BELIEVE"] = "BELIEF"
    token_dict["DREAMED"] = "DREAMT"
    token_dict["DREAMS"] = "DREAMT"

    # Make a list of it
    if token_dict.get(token) is not None:
        return token_dict.get(token)
    return None


def get_name(text):

    stopwords = nltk.corpus.stopwords.words('english')
    newstopwords = ['hi', 'there', 'whatsup', 'hey', 'hello']
    stopwords = [clean_text(word) for word in stopwords]
    stopwords.extend(newstopwords)
    text = text.strip()
    text = clean_text(text)
    if text.upper() == "NA":
        return "user"
    if text != "":
        text = clean_text(text)
        tokens = word_tokenize(text)
        tokens_tagged = nltk.pos_tag(tokens)
        tokens_tagged = [token for token in tokens_tagged if token[0].lower() not in set(stopwords)]

        if len(tokens_tagged) != 0:
            for (word, tag) in tokens_tagged:
                if tag in ['NN', 'NNP'] and word != 'Eliza':  # If the word is a proper noun
                    name = word
                    if tag == 'NNP':
                        break
                elif tag != 'NNP':
                    name = "User"
        else:
            name = "User"
    else:
        name = "User"
    return name

def get_greetings():
    greetings = ["Hello I am Eliza, what is your name?", "Hey I am Eliza, what is your name?",
                 "Hello this is Eliza, what is your name?", "Hello this is Eliza, lets get started with your name."]

    return f"{greetings[random.randint(0, len(greetings)) - 1]}\n"+"If you do not wish to give your name just enter " \
                                                                   "\'NA\'"
def get_helptext(user_name):
    help_text = ["How can I help you today?", "What do you want to talk about?", "How do you feel today?"]
    return f"Hi {user_name}! {help_text[random.randint(0, len(help_text)) - 1]}"

def process_user_input(user_input):
    global RANK
    global KEY_STACK
    global REPLIES

    try:
        REPLIES = []
        KEY_STACK = []
        RANK = 0

        if user_input.lower().strip() == "quit":
            return "Thank you for talking to me. If you need me anytime I am just a click away!!\nbye"

        # Replies are based on first sentence only if a user enters more than 1 sentence.
        user_input = user_input.replace(";", ',')
        user_input = sent_tokenize(user_input)[0].split(',')[0]
        user_input = clean_text(user_input)
        input_tokens = word_tokenize(user_input.strip().upper())

        transformation_dict = dict()
        for token in input_tokens:
            token_rank = get_rank(token)
            if token_rank == "TOKEN_NOT_FOUND" and chatbot_rules['TRANSFORMATION'].get(token) is not None:
                token_transformation = chatbot_rules['TRANSFORMATION'].get(token)
                transformation_dict[token_transformation] = token
                get_rank(token_transformation)

        # If there are no keywords present in user input
        if len(KEY_STACK) == 0:
            reply = get_reply("NONE", user_input)

        for key in KEY_STACK:
            if transformation_dict.get(key) is not None:
                inp_text = user_input.replace(transformation_dict.get(key), key)
            else:
                inp_text = user_input

            reply = get_reply(key, inp_text.upper())
            if reply.upper() == "DONT_SEARCH_FURTHER":
                break
            if reply.upper() in ["DECOMPOSITION_RULE_NOT_FOUND", "MATCH_NOT_FOUND",
                         "NEXT_KEY"] or reply is None or reply.lower() == 'none':
                reply = get_reply("NONE", user_input)
    except:
        reply = "Uh-oh!, somethings broken. Please send feedback to the admin regarding this to make me better."
    print(KEY_STACK )
    print(REPLIES)
    reply = REPLIES[0]
    return reply
