# -*- coding: utf-8 -*-
"""HateSpeechDetection_Project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1v0HvEe9xe1OylKrKH3lcQecrlL5mEvPl

# Defining the Question

### a) Specifying the Question

> Create a cross-lingual machine learning model focused on Political Hate Speech in Kenya which classifies whether an online post is deemed hate speech and the severity(sub-class) of it if so or not not hate speech (normal speech).

### b) Defining the Metric for Success

> An overall classification accuracy of 80% and Hate Class Recall of 70%.

### c) Understanding the context

> In an increasingly digital era where online social interactions are considered part of the social context, it is proving inevitable that machine learning should be used to protect people from harmful content. This has been evidenced by the multitude of instances where hate speech propagated online (mostly based on misinformation) has led to physical injury and loss of lives across the world. Government institutions should now consider online interactions as spaces where potential crimes may occur just like in the physical world.


> The goal of identifying hate speech efficiently and accurately irrespective of language is becoming a necessity. Countries like Kenya amongst other African nations have experienced the consequences of not dealing with hate speech as evidenced in previous years. Agencies such as the National Cohesion & Integration Commission were formed to help with this. Section 13 of National Cohesion and Integration Act(2008) outlines what is considered hate speech. In combination with the act an automated way of flagging hate speech would prove helpful for the institution given the country’s context which may not be similar to other countries meaning posts may not be picked/flagged by social media companies such as Twitter and Facebook as a result.


> Political hate speech is the greatest area of concern in regards to Kenya and thus we’ll be our area of focus. Looking at whether a post is Hate Speech or Normal Speech and it's severity (sub-class).

### d) Recording the Experimental Design

> The following design was used:


* Data importation
* Data Reading & Pre-processing
* EDA
* Unsupervised Topic Modeling
* Semi-Supervised Hate Speech Detection
  - Optimization/Tuning

### e) Data Relevance

> This was evaluated against the metric of success (after implementation of solution)

## Importing the libraries
"""

#@title lib installation
#installing transformers
!pip install transformers==3.1.0

#installing happytransformer
!pip install happytransformer

#tweet-preprocessor installation
!pip install tweet-preprocessor

#ekphrasis installation
!pip install ekphrasis

#emot installation
!pip install emot

#demoji installation
!pip install demoji

#Import libs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import re
import preprocessor as tweet_proc
import demoji
from transformers import pipeline
from happytransformer import HappyTextClassification
from ekphrasis.classes.segmenter import Segmenter
from emot.emo_unicode import UNICODE_EMO, EMOTICONS
from sklearn.model_selection import train_test_split

"""## Importing the Dataset

"""

#load dataset
tweets_df = pd.read_csv('/content/sample_dataset_eagles.csv')

#check head
tweets_df.head()

#check tail
tweets_df.tail()

#check number of records
tweets_df.shape

#checking column types
tweets_df.info()

#checking summary stats
tweets_df.describe()

#checking for nulls
tweets_df.isnull().sum()

#drop nulls
tweets_df = tweets_df.dropna()

#checking for nulls
tweets_df.isnull().sum()

#check number of records
tweets_df.shape

#check duplicates
tweets_df.duplicated().sum()

#drop duplicates
tweets_df = tweets_df.drop_duplicates()

#check number of records
tweets_df.shape

"""## Pre-processing

> In this section we'll find instances of usersnames, numbers, hashtags, URLs and common emoticons and replace them with the tokens: "user","number","hashtag","url","emoticon".

> We also shorten elongated words into standard format e.g yeeeessss to yes. The hashtags that include some tokens without spacing between them, we replace them by their textual
counterparts e.g. converting hashtag “#notsexist” to “not sexist”. 

> Punctuation marks, extra delimiting characters are removed, but stop words are kept because our proposed model trains the sequence of words in a text directly. We also convert all tweets to lower case.
"""

#change column name
tweets_df.rename(columns={'hate_speech(1=hspeech, 0=nohspeech)': "hate_speech"}, inplace=True)

# #create copy to work with
# tweet_df = tweets_df.copy(deep=True)

# #drop default hashtag column and derive from tweet
# tweet_df = tweet_df.drop("hashtags", axis=1)

# #extract tags from tweets
# tweet_df['hashtag'] = tweet_df['tweet'].apply(lambda x: re.findall(r"#(\w+)", x))

# #using tweet preprocessor to clean tweets
# #set options
# tweet_proc.set_options(tweet_proc.OPT.URL, tweet_proc.OPT.EMOJI,tweet_proc.OPT.MENTION,tweet_proc.OPT.HASHTAG,tweet_proc.OPT.RESERVED,
#                        tweet_proc.OPT.SMILEY)

#forming a separate feature for cleaned tweets
#create empty col
#tweet_df['text'] = ''
#tweet_df['text'] = str(tweet_df['tweet'])
# for i,v in enumerate(tweet_df['tweet']):
#   tweet_df.loc[i,"text"] = tweet_proc.clean(v)

#segment any hashtags
#seg_tw = Segmenter(corpus="twitter")
#tweet_df['hashtag'] =str(tweet_df['hashtag'])
# a = []
# for i in range(0,len(tweet_df)):
#  if tweet_df['hashtag'][i] != a:
#   listToStr1 = ' '.join([str(elem) for elem in tweet_df['hashtag'][i]])
#   tweet_df.loc[i,'Segmented#'] = seg_tw.segment(listToStr1)

#change to lower case all the  tweets and remove numbers
# def preprocess_data(data):
#   #Removes Numbers
#   #data = data.astype(str).str.replace('\d+', '')
#   lower_text = data.str.lower()

# prep_tweets = preprocess_data(tweet_df['text'])
# tweet_df['text'] = prep_tweets


# #remove punctuation
# def remove_punctuation(words):
#   new_words = []
#   for word in words:
#     new_word = re.sub(r'[^\w\s]', '', (word))
#     if new_word != '':
#       new_words.append(new_word)
#   return new_words

#   words = lower_text.apply(remove_punctuation)
#   return pd.DataFrame(words)

# prep_tweets = remove_punctuation(tweet_df['text'])
# tweet_df['text'] = prep_tweets


#view cleaned df
#tweet_df.head()

#mentioned tokens: <user>,<number>,<hashtag>,<url>,<emoticon>
#Pre-process tweets
#using tweet-preprocessor3 lib for tweet tokenization

# to leverage word statistics from Twitter
#seg_tw = Segmenter(corpus = "twitter")
#cleaning the following:
# URL	-> .OPT.URL
# Mention	-> .OPT.MENTION
# Hashtag	-> .OPT.HASHTAG
# Reserved Words	-> .OPT.RESERVED
# Emoji	-> .OPT.EMOJI
# Smiley	-> .OPT.SMILEY


#set options
tweet_proc.set_options(tweet_proc.OPT.URL, tweet_proc.OPT.EMOJI,tweet_proc.OPT.MENTION,tweet_proc.OPT.HASHTAG,tweet_proc.OPT.RESERVED,
                       tweet_proc.OPT.SMILEY)


#create a txt file of the tweet list to use in the clean tweets package

#define a unique delimiter for each record(tweet)
DELIMITER = "|"

#make a list of the tweet col
tweet = list(tweets_df['tweet'])

#write to txt file named tweet
with open('tweet.txt', 'w') as outfile:
    writer = csv.writer(outfile, delimiter=DELIMITER)
    writer.writerow(tweet)

#read the txt file to see row
with open('tweet.txt', 'r') as infile:
    reader = csv.reader(infile, delimiter=DELIMITER)
    for row in reader:
        print(row)

#use the method clean_file to clean the tweets and save
tweet_proc.clean_file("/content/tweet.txt")

#import the cleaned txt file as a df
df = pd.read_csv("/content/4eAXsoe9JIsp_tweet.txt",delimiter=DELIMITER , header=None)

#transpose to have cols and rows correct
df = df.transpose()

#check shape to confirm
df.shape

#rename col of tweet df
df.rename(columns={0: "cleaned_tweet"}, inplace=True)

# #create copy to work with
tweet_df = tweets_df.copy(deep=True)

#reset index
tweet_df.reset_index(inplace=True)

#append it as a column back to the original dataframe
tweet_df['cleaned_tweet']= df

#punctuation
tweet_df['cleaned_tweet'] = tweet_df['cleaned_tweet'].str.replace('[^\w\s]', '').astype(str) 

#remove digits
twl_1 = list(tweet_df['cleaned_tweet'])
no_num = []
for w in range(len(twl_1)):
  remove_num = re.sub(r'\d+', '', twl_1[w])
  no_num.append(remove_num)

#create a dataframe to hold the new tweets
no_num_df = pd.DataFrame(no_num, columns=['no_num_twt'])

#append it as a column back to the original dataframe
tweet_df['no_num_twt']= no_num_df

#lower case
tweet_df['no_num_twt'] = tweet_df['no_num_twt'].apply(lambda x: x.lower())

#drop old tweet col before cleaning
tweet_df = tweet_df.drop(['tweet','cleaned_tweet','index'], axis=1)

#rename col of tweet df
tweet_df.rename(columns={'no_num_twt': "tweet"}, inplace=True)

#preview new df
tweet_df.tail()



"""## Feature Engineering"""

# use tweet-preprocessor to include some useful information
# fields which can act as features for our classifiers
# Include the hashtag text after segmenting into meaningful tokens using the ekphrasis segmenter for the twitter corpus

# save information such as URLs, name mentions, quantitative values and smileys
# extract emojis and processed using emoji2vec to obtain a semantic vector representing the particular emoji

"""# Exploratory Data Analysis"""

#proportion of hate speech

# let us plot histograms to visualize patterns in the data
tweet_df.hist(figsize = (20,10))
plt.show()

# Boxplots to Visualize outliers of our numerical columns 
plt.figure(figsize = (20,10))
ax = sns.boxplot(data=tweet_df, orient="v", palette="Set2")
plt.title('Checking for outliers using boxplots')
# The boxplots below indicate the outliers in each of the numerical columns

# let us see how the labels are distributed in our dataset
# plt_hate = tweet_df.copy(deep=True)
# plt_hate.rename
# tweets_df.rename(columns={'hate_speech(1=hspeech, 0=nohspeech)': "hate_speech"}, inplace=True)


#plot countplot
plt.figure(figsize=(10,5))
sns.countplot(x="hate_speech", data = tweet_df)
plt.title("Number of Hate Speech Posts")

plt.show()


# neutral labels are the highest in our data



# # extracting the number of examples of each class
# hate = tweet_df[tweet_df['hate_speech'] == 1]
# not_hate = tweet_df[tweet_df['hate_speech'] == 0]

# # bar plot of the 3 classes
# #plt.rcParams['figure.figsize'] = (7, 5)
# plt.bar(hate, label="Hate Speech", color='red')
# plt.bar(not_hate, label="Not Hate Speech", color='blue')
# plt.legend()
# plt.ylabel('Number of examples')
# plt.title('Propertion of examples')
# plt.show()

# Most common words
from wordcloud import WordCloud
from nltk import FreqDist
#Frequency of words
fdist = FreqDist(tweet_df['hashtags'])
#WordCloud
wc = WordCloud(width=800, height=400, max_words=50).generate_from_frequencies(fdist)
plt.figure(figsize=(12,10))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

"""# Implementing the Solution

## Unsupervised Topic Modeling

### Build pipeline for text classification
"""

#Instantiate class pipeline from transformers
#classifier = pipeline("zero-shot-classification")
# classifier = pipeline("zero-shot-classification", device=0) # to utilize GPU

# Zero-shot classification in 100 languages
# A pipeline for languages other than English,
# a trained cross-lingual model on top of XLM RoBERTa:

classifier = pipeline("zero-shot-classification", model='joeddav/xlm-roberta-large-xnli')

#multi-lingual
sequence = "Wewe ni mavi ya kuku"
candidate_labels = ["violent", "offensive", "profane"]

res = classifier(sequence, candidate_labels,multi_label=False)

print(res['labels'])
print(res['scores'])

print(res['labels'])
print(res['scores'])

# for multi-class classification, we pass multi_class=True. 
# In this case, the scores will be independent, but each will fall between 0 and 1.

#e.g.
#sequence = "Who are you voting for in 2020?"

#candidate_labels = ["politics", "public health", "economics", "elections"]

#classifier(sequence, candidate_labels, multi_class=True)


#candidate_labels = ["politics", "public health", "economics", "elections"]

candidate_labels = ["violent", "offensive", "profane"]


# #cluster tweets to sub-classes
# twl_1 = list(tweet_df['tweet'])
# sub_group = []
# for t in range(len(twl_1)):
#   preds = classifier(twl_1, candidate_labels, multi_label=True)
#   sub_group.append(preds)

#create a dataframe to hold the new tweets
#no_num_df = pd.DataFrame(no_num, columns=['no_num_twt'])

#from transformers import pipeline english only
#classifier = pipeline("zero-shot-classification")

sequence = "Wewe ni mavi ya kuku"
candidate_labels = ["violent", "offensive", "profane"]

classifier(sequence, candidate_labels,multi_label=True)

#doing a list
>>> results = classifier(["We are very happy to show you the 🤗 Transformers library.",
...            "We hope you don't hate it."])
>>> for result in results:
...     print(f"label: {result['label']}, with score: {round(result['score'], 4)}")
label: POSITIVE, with score: 0.9998
label: NEGATIVE, with score: 0.5309

"""## Semi-Supervised Hate Speech Detection

### Optimization/Tuning
"""

#Create A HappyTextClassification Object (ROBERTA or BERT)
#happy_tc = HappyTextClassification("ROBERTA", "roberta-base")

#Create A HappyTextClassification Object (ROBERTA or BERT)
#Bert used with 2 labels (Hate/Non_hate)
happy_tc = HappyTextClassification("BERT", "Hate-speech-CNERG/dehatebert-mono-english", 2)

#Hate-speech-CNERG/bert-base-uncased-hatexplain
#Create A HappyTextClassification Object (ROBERTA or BERT)
#happy_tc = HappyTextClassification("BERT", "Hate-speech-CNERG/bert-base-uncased-hatexplain")

#predict hate speech or not
result = happy_tc.classify_text("xx xxx")
print(result)
print(result.label)
print(result.score)

"""### Train & Eval"""

#create a train_eval file from the dataset
#rename cols of tweet df
tweet_df.rename(columns={"hate_speech": "label","tweet": "text" }, inplace=True)

#convert label column to int
tweet_df.label = tweet_df.label.astype(int)

# split the data into train and test set
train_eval, test = train_test_split(tweet_df, test_size=0.2, random_state=101, shuffle=False)

#extract text and label
train_eval = train_eval[['text', 'label']]
test = test[['text', 'label']]

#save dfs to csv
train_eval.to_csv("train-eval.csv")
test.to_csv("test.csv")

#fine tune to the dataset
#happy_tc.train("../../data/tc/train-eval.csv")

#fine tune to the dataset
happy_tc.train("/content/train-eval.csv")

#eval the fine tuned model
result = happy_tc.eval("/content/train-eval.csv")
print(type(result))  # <class 'happytransformer.happy_trainer.EvalResult'>
print(result)  # EvalResult(eval_loss=0.007262040860950947)
print(result.loss)  # 0.007262040860950947



#test the model
result = happy_tc.test("/content/test.csv")
print(type(result))  # <class 'list'>
print(result)  # [TextClassificationResult(label='LABEL_1', score=0.9998401999473572), TextClassificationResult(label='LABEL_0', score=0.9772131443023682)...
print(type(result[0]))  # <class 'happytransformer.happy_text_classification.TextClassificationResult'>
print(result[0])  # TextClassificationResult(label='LABEL_1', score=0.9998401999473572)
print(result[0].label)  # LABEL_1

"""##Fine-tune"""

!pip install nlp

!pip install optuna

!pip install tqdm

"""#Transformer Libs"""

#import libs
#import nlp
import optuna
import argparse
import transformers
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup, DistilBertModel, DistilBertConfig
import torch
import numpy as np
import pandas as pd
import seaborn as sns
import torch.nn.functional as F
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report,f1_score, precision_score, recall_score, average_precision_score
from collections import defaultdict
from textwrap import wrap
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

"""> trial another"""

#creating dataset for BERT
#split dataset
#df = pd.read_csv("clean")
tw = tweets_df.copy(deep=True)

#reset index
tw.reset_index(inplace=True)

#convert label column to int
tw.hate_speech = tw.hate_speech.astype(int)


# Creating training dataframe according to BERT by adding the required columns
df_bert = pd.DataFrame({
    'id':range(len(tw)),
    'label':tw.iloc[:,3],
    'alpha':['a']*tw.shape[0],
    'text': tw.iloc[:,2].replace(r'\n', ' ', regex=True)
})



# split the data into train and test set
train_dataset, test_dataset = train_test_split(df_bert, test_size=0.2, random_state=101, shuffle=False)

# Splitting training data file into *train* and *dev*
df_bert_train, df_bert_dev = train_test_split(df_bert, test_size=0.1)

df_bert_train.head()

#test dataset
# Creating test dataframe according to BERT
df_bert_test = pd.DataFrame({
    'id':range(len(test_dataset)),
    'text': test_dataset.iloc[:,3].replace(r'\n', ' ', regex=True)
})

df_bert_test.head()

#saving as tsv

# Saving dataframes to .tsv format as required by BERT
df_bert_train.to_csv('train.tsv', sep='\t', index=False, header=False)
df_bert_dev.to_csv('dev.tsv', sep='\t', index=False, header=False)
df_bert_test.to_csv('test.tsv', sep='\t', index=False, header=False)

#add emojis to tokenizer
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
s =" 😃 hello how are you"

tokenizer.add_tokens(["😃" ,"😡","🤬", "🖕","💯"])
print(tokenizer.tokenize(s))

#increase vocab
# Let's see how to increase the vocabulary of Bert model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

num_added_toks = tokenizer.add_tokens(["😃" ,"😡","🤬", "🖕","💯"])
print('We have added', num_added_toks, 'tokens')
 # Notice: resize_token_embeddings expect to receive the full size of the new vocabulary, i.e., the length of the tokenizer.
model.resize_token_embeddings(len(tokenizer))

"""#Prototype Model"""

#split dataset
#df = pd.read_csv("clean")
tw = tweets_df.copy(deep=True)

#reset index
tw.reset_index(inplace=True)

#rename cols of tweet df
tw.rename(columns={"hate_speech": "label","tweet": "text" }, inplace=True)

#convert label column to int
tw.label = tw.label.astype(int)

class_names = ["Normal", "Hate"]

#view data dist
ax = sns.countplot(x = tw['label'])
plt.xlabel('Speech Type')
ax.set_xticklabels(class_names)
plt.show()

"""###Pre-processing"""

from transformers import DistilBertTokenizerFast
#tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

#choose sequence length
token_lens = []
for txt in tw.text:
  tokens = tokenizer.encode(txt, max_length=512, truncation=True)
  token_lens.append(len(tokens))

#plot dist to det length
sns.displot(token_lens)
plt.xlim([0, 256])
plt.xlabel('Token count')
plt.show()

"""##funcs"""

#create dataset
class KenyaHateSpeechDataset(Dataset):
  def __init__(self, reviews, targets, tokenizer, max_len):
    self.reviews = reviews
    self.targets = targets
    self.tokenizer = tokenizer
    self.max_len = max_len
  def __len__(self):
    return len(self.reviews)
  def __getitem__(self, item):
    review = str(self.reviews[item])
    target = self.targets[item]
    encoding = self.tokenizer.encode_plus(
      review,
      add_special_tokens=True,
      max_length=self.max_len,
      return_token_type_ids=False,
      padding="max_length",
      return_attention_mask=True,
      return_tensors='pt',
      truncation=True
    )
    return {
      'review_text': review,
      'input_ids': encoding['input_ids'].flatten(),
      'attention_mask': encoding['attention_mask'].flatten(),
      'targets': torch.tensor(self.targets[item], dtype=torch.long)
    }

#we'll set constants
MAX_LEN = 140
BATCH_SIZE=16
EPOCHS = 5

#split data
RANDOM_SEED = 101
df_train, df_test = train_test_split(tw, test_size=0.2, random_state=RANDOM_SEED)
df_val, df_test = train_test_split(df_test, test_size=0.5, random_state=RANDOM_SEED)
df_train.shape, df_val.shape, df_test.shape

def create_data_loader(df, tokenizer, max_len, batch_size):
  ds = KenyaHateSpeechDataset(
    reviews=df.text.to_numpy(),
    targets=df.label.to_numpy(),
    tokenizer=tokenizer,
    max_len=max_len,
    
  )
  return DataLoader(
    ds,
    batch_size=batch_size,
    num_workers=2
  )

#create dataloaders for each dataset
train_data_loader = create_data_loader(df_train, tokenizer, MAX_LEN, BATCH_SIZE)
val_data_loader = create_data_loader(df_val, tokenizer, MAX_LEN, BATCH_SIZE)
test_data_loader = create_data_loader(df_test, tokenizer, MAX_LEN, BATCH_SIZE)

#view example batch
data = next(iter(train_data_loader))
data.keys()

print(data['input_ids'])
print(data['input_ids'].shape)
print(data['attention_mask'].shape)
print(data['targets'].shape)

#load pre-trained model
# from transformers import BertConfig
# config = BertConfig.from_pretrained('bert-base-uncased')
# config.num_labels

PRE_TRAINED_MODEL_NAME = 'bert-base-uncased'
#PRE_TRAINED_MODEL_NAME = 'distilbert-base-uncased'
bert_model = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME,return_dict=False)
#bert_model = DistilBertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)

"""##Building Classifier"""

#CUDA_LAUNCH_BLOCKING=1

class HateSpeechClassifier(nn.Module):
  def __init__(self, n_classes=2):
    super(HateSpeechClassifier, self).__init__()
    self.bert = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME,return_dict=False)
    #config = DistilBertConfig.from_pretrained( PRE_TRAINED_MODEL_NAME, output_hidden_states=True)    
    #self.bert = DistilBertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
    self.drop = nn.Dropout(p=0.3)
    self.out = nn.Linear(self.bert.config.hidden_size,n_classes)
    self.softmax = nn.Softmax(dim=1) #n_classes hapo juu instead of 1
    #self.argmax = np.argmax()
    #self.sigmoid = nn.Sigmoid()

  def forward(self, input_ids, attention_mask):
    _, pooled_output = self.bert(
      input_ids=input_ids,
      attention_mask=attention_mask,
      #output_hidden_states=True,
      return_dict=False
    )
    #return_dict=False
    output = self.drop(pooled_output)
    output = self.out(output)
    return self.softmax(output)
    #return self.out(output)
    #return self.sigmoid(output)

#instantiate custom model
#device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = HateSpeechClassifier(len(class_names))
model = model.to(device)

#testing on our tokens
input_ids = data['input_ids'].to(device)
attention_mask = data['attention_mask'].to(device)

print(input_ids.shape)
print(attention_mask.shape)

#using model to predict as test before training
model(input_ids, attention_mask)

"""##training"""

#EPOCHS = 2
optimizer = AdamW(model.parameters(), lr=2e-5, correct_bias=False)

total_steps = len(train_data_loader) * EPOCHS

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps = 0,
    num_training_steps = total_steps
)

loss_fn = nn.CrossEntropyLoss().to(device)
#loss_fn = nn.BCEWithLogitsLoss().to(device)

#help func to training epoch
def train_epoch(
    model,
    data_loader,
    loss_fn,
    optimizer,
    device,
    scheduler,
    n_examples
):

  model = model.train()

  losses = []
  correct_predictions = 0

  for d in data_loader:
    input_ids = d['input_ids'].to(device)
    attention_mask = d['attention_mask'].to(device)
    targets = d['targets'].to(device)
    #targets = targets.unsqueeze(1)
    #targets = targets.long()

    outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask
    )

    _, preds = torch.max(outputs, dim=1)
    loss = loss_fn(outputs, targets)

    correct_predictions += torch.sum(preds == targets)
    losses.append(loss.item())

    loss.backward()
    nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    scheduler.step()
    optimizer.zero_grad()

  return correct_predictions.double() / n_examples, np.mean(losses)

#eval current model

def eval_model(model, data_loader, loss_fn,device,n_examples):
  model = model.eval()

  losses = []
  correct_predictions = 0

  with torch.no_grad():
    for d in data_loader:

      input_ids = d['input_ids'].to(device)
      attention_mask = d['attention_mask'].to(device)
      targets = d['targets'].to(device)
      #targets = targets.unsqueeze(1)
      #targets = targets.type_as(output)

      # outputs = model(
      #     input_ids=input_ids,
      #     attention_mask=attention_mask

      outputs = model(
          input_ids=input_ids,
          attention_mask=attention_mask

      )

      _, preds = torch.max(outputs, dim=1)
      loss = loss_fn(outputs, targets)

      correct_predictions += torch.sum(preds == targets)
      losses.append(loss.item())

  return correct_predictions.double() / n_examples, np.mean(losses)

# Commented out IPython magic to ensure Python compatibility.
# #hist dict to store loss and accuracy
# %%time
# 
# history = defaultdict(list)
# best_accuracy = 0
# 
# for epoch in range(EPOCHS):
# 
#   print(f'Epoch {epoch + 1}/{EPOCHS}')
#   print('-' * 10)
# 
#   train_acc, train_loss = train_epoch(
#       model,
#       train_data_loader,
#       loss_fn,
#       optimizer,
#       device,
#       scheduler,
#       len(df_train)
#   )
# 
#   print(f'Train loss {train_loss} accuracy {train_acc}')
# 
# 
#   val_acc, val_loss = eval_model(
#       model,
#       val_data_loader,
#       loss_fn,
#       device,
#       len(df_val)
#   )
# 
#   print(f'Val loss {val_loss} accuracy {val_acc}')
#   print()
# 
#   history['train_acc'].append(train_acc)
#   history['train_loss'].append(train_loss)
# 
#   history['val_acc'].append(val_acc)
#   history['val_loss'].append(val_loss)
# 
#   if val_acc > best_accuracy:
#     torch.save(model.state_dict(), 'model.bin')
#     best_accuracy = val_acc
# 
#

#view the training
plt.plot(history['train_acc'], label='train accuracy')
plt.plot(history['val_acc'], label='validation accuracy')
plt.title('Training history')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.ylim([0, 1])

#download the saved model
#!gdown --id https://drive.google.com/uc?id=/content/model.bin

#load model
model = HateSpeechClassifier(len(class_names))
model.load_state_dict(torch.load('model.bin'))
model = model.to(device)

"""##evaluation"""

def get_predictions(model, data_loader):
  model = model.eval()

  review_texts = []
  predictions = []
  prediction_probs = []
  real_values = []

  with torch.no_grad():
    for d in data_loader:

      texts = d['review_text']
      input_ids = d['input_ids'].to(device)
      attention_mask = d['attention_mask'].to(device)
      targets = d['targets'].to(device)

      outputs = model(
          input_ids=input_ids,
          attention_mask=attention_mask
      )

      _, preds = torch.max(outputs, dim=1)

      review_texts.extend(texts)
      predictions.extend(preds)
      prediction_probs.extend(outputs)
      real_values.extend(targets)

    predictions = torch.stack(predictions).cpu()
    prediction_probs = torch.stack(prediction_probs).cpu()
    real_values = torch.stack(real_values).cpu()

    return review_texts, predictions, prediction_probs,real_values

#get test accuracy and loss
test_acc, test_loss = eval_model(model, test_data_loader, loss_fn,device,len(df_test))

#accuracy on test set
test_acc

#call helper func
y_review_texts, y_pred,y_pred_probs,y_test = get_predictions(model, test_data_loader)

#eval report
print(classification_report(y_test,y_pred, target_names=class_names))

#confusion matrix of model
def show_confusion_matrix(confusion_matrix):
  hmap = sns.heatmap(confusion_matrix, annot=True, fmt="d", cmap="Blues")
  hmap.yaxis.set_ticklabels(hmap.yaxis.get_ticklabels(), rotation=0, ha='right')
  hmap.xaxis.set_ticklabels(hmap.xaxis.get_ticklabels(), rotation=30, ha='right')
  plt.ylabel('True Type of Speech')
  plt.xlabel('Predicted Type of Speech');
cm = confusion_matrix(y_test, y_pred)
df_cm = pd.DataFrame(cm, index=class_names, columns=class_names)
show_confusion_matrix(df_cm)

#predict new tweet
#give index
idx = 2
review_text = y_review_texts[idx]
true_sentiment = y_test[idx]

pred_df = pd.DataFrame(
    {
    "class_names": class_names,
    "values": y_pred_probs[idx]
    }
)

#use wrap module
print("\n".join(wrap(review_text)))
print()
print(f'Type of Speech: {class_names[true_sentiment]}')

#plot preds
sns.barplot(x="values", y="class_names", data=pred_df, orient="h")
plt.ylabel("sentiment")
plt.xlabel("probability")
plt.xlim([0,1])

"""###predict raw text"""

#input txt as string
review_text = "the country is going to the dogs because of you people"

#encode txt
encoded_review = tokenizer.encode_plus(
    review_text,
    max_length=MAX_LEN,
    add_special_tokens=True,
    return_token_type_ids=False,
    padding="max_length",
    return_attention_mask=True,
    return_tensors='pt'
)

#move to device
input_ids = encoded_review['input_ids'].to(device)
attention_mask = encoded_review['attention_mask'].to(device)

#run through model to get predictions
output = model(input_ids,attention_mask)
_, prediction = torch.max(output, dim=1)

#print review text and class
print(f'Tweet: {review_text}')
print(f'Class of Speech: {class_names[prediction]}')

"""# Challenging the Solution

# Follow up questions

## a) Did we have the right data?

## b) Do we need other data to answer our question?

## c) Did we have the right question?
"""