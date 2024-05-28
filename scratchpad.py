import plotly.graph_objects as go
import dataIO 
from elasticsearch import Elasticsearch
from urllib.parse import urlparse


import sqlalchemy
import pandas as pd
import os
import json


# elastic search test
def searchbox_connect():
    
    url = urlparse("https://paas:***REMOVED***")

    print(url.username, url.password)
    ######## test
    es = Elasticsearch(
        ["https://paas:***REMOVED***"],
        http_auth=(url.username, url.password),
        scheme=url.scheme,
        port=url.port,
    )
    return es

es = searchbox_connect()


query1 = {
    "query" : { "match" :{"source": "ALSPAC"}}
}
query2 = {
    "query": {"match": {"table_name": "COVID"}}
}
query3 = {
    "query": {"regexp": {"table": 
                            {"value" : ".*COVID.*",
                            "flags" : "ALL",
                            "case_insensitive": "true",
                            "max_determinized_states": 10000,
                                   }}}
}
query4 = {
    "query": {
        "bool" : {
            "must" : {
                "match" : { "source" : "BCS70" }
            },
            "should" : {
                "regexp": {"table": 
                                {"value" : ".*COVID.*",
                                "flags" : "ALL",
                                "case_insensitive": "true",
                                "max_determinized_states": 10000,
                                    }}
            },
        }
    }
}


query5 = {
    "query": {
        "bool" : {
            "must_not" : {
                "match" : { "source" : "BCS70"}
            },
            
            "should" : {
                "regexp": {"table": 
                                {"value" : ".*COVID.*",
                                "flags" : "ALL",
                                "case_insensitive": "true",
                                "max_determinized_states": 10000,
                                    }}
            },
        }
    }
}
query6 = {
    "query": {"match": {"long_desc": "mothers"}}
}

query7 = {
    "query" : {
        "bool" : {
            "should" : [
                {"range": {
                    "lf" : {
                        "gte" : "40", # lower range
                        "lte" : "100" # upper range
                    },
                }},
                {"range": {
                    "q2" : {
                        "gte" : "40", # lower range
                        "lte" : "100" # upper range
                    },
                }},
                {"range": {
                    "uf" : {
                        "gte" : "40", # lower range
                        "lte" : "100" # upper range
                    },
                }},
            ],
        }
    }
}
query72 = {
    "query" :{
        "range": {
            "q2" : {
                "gte" : 0, # lower range
                "lte" : 100 # upper range
            }
        }
    }
}


query8 = {
    "query" : {
        "bool" : {
            "should" : [
                {"range": {
                    "collection_start" : {
                        "gte" : "01/2000",
                        "lte" : "01/2025",
                        "format" : "MM/YYYY"
                    }
                }},
                {"range": {
                    "collection_end" : {
                        "gte" : "01/2000",
                        "lte" : "01/2025",
                        "format" : "MM/YYYY"
                    }
                }}
            ]
        }
    }
}


match_all = {"query": {"match_all": {}}}

'''
How to query each bit:
source: match
source_name:  match
table: regex
table_name: match
long_desc : match
topic_tags : match
collection_start / end : range date
lf, uf : range numeric
aims : match
type : match
'''

x = "text"
all_query = {
    "query": {
        "bool" : {
            "filter":[{
                "bool" : {
                    "should" : [
                        {"term" : { "source" : "ALSPAC"}},
                        {"term" : { "source" : "BCS70"}}
                    ],
                }
            }],
            
            "must" : [{
                "bool" : {
                    "should" : [
                        { "regexp": {"table": 
                                    {"value" : ".*COVID.*",
                                    "flags" : "ALL",
                                    "case_insensitive": "true",
                                    "max_determinized_states": 10000,
                                }
                            } 
                        },
                        { "match": {"table_name": "COVID"}},
                        { "match": {"long_desc": "mothers"}},
                        { "match": {"topic_tags": "mothers"}},
                        { "match": {"Aims": "mothers"}},
                        { "match": {"Themes": "mothers"}},

                        {"range": {
                            "lf" : {
                                "gte" : "40", # lower range
                                "lte" : "100" # upper range
                            },
                        }},
                        {"range": {
                            "q2" : {
                                "gte" : "40", # lower range
                                "lte" : "100" # upper range
                            },
                        }},
                        {"range": {
                            "uf" : {
                                "gte" : "40", # lower range
                                "lte" : "100" # upper range
                            },
                        }},

                        {"range": {
                            "collection_start" : {
                                "gte" : "01/2000",
                                "lte" : "01/2025",
                                "format" : "MM/YYYY"
                            }
                        }},
                        {"range": {
                            "collection_end" : {
                                "gte" : "01/2000",
                                "lte" : "01/2025",
                                "format" : "MM/YYYY"
                            }
                        }}
                    ],
                } 
            },
            ],
            ""
            "must_not" : [{
                "bool" : {
                    "should" : [
                        {"term" : { "source" : "BCS70"}}
                    ],
                }
            }],
        },
    }
}

test_query = {"query": {"bool": {"filter": [
                {"bool": {"should": [
                            {"term": {"source": "ALSPAC"
                                }
                            },
                            {"term": {"source": "BCS70"
                                }
                            },
                            {"term": {"source": "BIB"
                                }
                            },
                            {"term": {"source": "ELSA"
                                }
                            },
                            {"term": {"source": "EPICN"
                                }
                            },
                            {"term": {"source": "EXCEED"
                                }
                            },
                            {"term": {"source": "FENLAND"
                                }
                            },
                            {"term": {"source": "GENSCOT"
                                }
                            },
                            {"term": {"source": "GLAD"
                                }
                            },
                            {"term": {"source": "MCS"
                                }
                            },
                            {"term": {"source": "NCDS58"
                                }
                            },
                            {"term": {"source": "NEXTSTEP"
                                }
                            },
                            {"term": {"source": "NICOLA"
                                }
                            },
                            {"term": {"source": "NIHRBIO_COPING"
                                }
                            },
                            {"term": {"source": "NSHD46"
                                }
                            },
                            {"term": {"source": "SABRE"
                                }
                            },
                            {"term": {"source": "TRACKC19"
                                }
                            },
                            {"term": {"source": "TWINSUK"
                                }
                            },
                            {"term": {"source": "UKHLS"
                                }
                            },
                            {"term": {"source": "nhsd"
                                }
                            },
                            {"term": {"source": "GEO"
                                }
                            }
                        ]
                    }
                }
            ], "must_not": [
                
            ], "must": [
                {"bool": {"should": [
                            {"range": {"lf": {"gte": 0, "lte": 100
                                    }
                                }
                            },
                            {"range": {"q2": {"gte": 0, "lte": 100
                                    }
                                }
                            },
                            {"range": {"uf": {"gte": 0, "lte": 100
                                    }
                                }
                            },
                            {"range": {"collection_start": {"gte": "01/1900", "lte": "01/2025", "format": "MM/YYYY"
                                    }
                                }
                            },
                            {"range": {"collection_end": {"gte": "01/1900", "lte": "01/2025", "format": "MM/YYYY"
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
}
r = es.search(index="index_spine", body=test_query, size = 1000)


for hit in r["hits"]["hits"]:
    print(hit["_source"]["source"], hit["_source"]["table"], hit["_source"]["table_name"])

print(r["hits"]["hits"])