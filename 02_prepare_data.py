import pandas as pd
import spacy
import swifter
from bs4 import BeautifulSoup
import os
import langdetect

nlp = spacy.load('ner_v1')

def get_num_entitites(text, enttype, max_len=4000, model=nlp):

    text = BeautifulSoup(text).get_text()
    doc = model(text[:max_len])
    entities = [entity.text for entity in doc.ents if entity.label_ == enttype]
    return(len(entities))

def get_num_entitites_from_raw(text, enttype, max_len=4000, model=nlp):

    doc = model(text[:max_len])
    entities = [entity.text for entity in doc.ents if entity.label_ == enttype]
    return(len(entities))

def get_language(textcell):
    try:
        text = BeautifulSoup(textcell, features="html.parser").get_text()
        language = langdetect.detect(text)
    except Exception as e:
        language = 'UNK'
    return language

def get_language_from_raw(text):
    try:
        language = langdetect.detect(text)
    except Exception as e:
        language = 'UNK'
    return language


def get_raw_text(textcell):
    try:
        text = BeautifulSoup(textcell, features="html.parser").get_text()
    except Exception as e:
        text = ''
    return text


def get_num_words(rawtext):
    vec = rawtext.split(" ")
    return len(vec)

# jobs from historical files
all_jobs = pd.read_feather('bucket_data/all_jobs.feather')
all_jobs['year'] = all_jobs['statistikk_aar_mnd'].str[:4]
all_jobs = all_jobs[['stillingsbeskrivelse_vasket', 'stillingstittel',  'bedrift_org_nr', 'year', 'statistikk_aar_mnd']]
all_jobs.rename(columns = {'stillingsbeskrivelse_vasket': 'description',
                 'stillingstittel': 'title',
                 'bedrift_org_nr': 'employer_orgnr'}, inplace=True)


# business register
er = pd.read_parquet('/Users/radbrt/Data/underenheter.parquet')
er = er[['orgnr', 'forradrkommnr', 'forradrkommnavn', 'nkode1', 'ansatte_antall']]

# jobs from API (read from mongodb)
api_jobs = pd.read_feather('bucket_data/ads_from_api.feather')
api_jobs['year'] = '2020'
api_jobs = api_jobs[['description', 'title', 'employer_orgnr', 'year', 'published']]

# nace labels
nace = pd.read_csv('data/nace.csv', names=["label", "code"], dtype='str')

jobs = pd.concat([all_jobs, api_jobs]).reset_index(drop=True)


jobs_er = pd.merge(er, jobs, left_on='orgnr', right_on='employer_orgnr')

jobs_er['raw_text'] = jobs_er['description'].swifter.apply(lambda x: get_raw_text(x))
jobs_er['lang'] = jobs_er['raw_text'].swifter.apply(lambda x: get_language_from_raw(x))
jobs_er['num_pferd'] = jobs_er['raw_text'].swifter.apply(lambda x: get_num_entitites_from_raw(x, 'PFERD'))
jobs_er['num_words'] = jobs_er['raw_text'].swifter.apply(lambda x: get_num_words(x))
jobs_er['code'] = jobs_er['nkode1'].str[:2]


jobs_er_nace = pd.merge(jobs_er, nace, on='code')

jobs_er_nace.to_feather('bucket_data/jobs_er.feather')
jobs_er_nace[['employer_orgnr', 'num_pferd', 'nkode1', 'num_words', 'year', 'lang', 'label', 'statistikk_aar_mnd']].to_feather('data/jobs_small.feather')
