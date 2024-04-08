import pandas as pd
import whoosh
from whoosh import fields, index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh import qparser
from whoosh.qparser import QueryParser
from whoosh.query import Term, Or, And
from whoosh.filedb.filestore import FileStorage
import time

storage_var = FileStorage("index_var")
storage_var.open_index()

storage_spine = FileStorage("index_spine")
storage_spine.open_index()


s = ""
include_dropdown = []
exclude_dropdown = []
page = 1

time0 = time.time()
ix_var = whoosh.index.open_dir('index_var')
ix_spine = whoosh.index.open_dir('index_spine')
searcher_var = ix_var.searcher()
searcher_spine = ix_spine.searcher()
print("setup = {}".format(time.time()-time0))



# 2. include dropdown
if include_dropdown:
    print("INCLUDE (TEMP LOCKED TO FIRST FOR DEBUG)")
    allow_q = whoosh.query.Term("source", include_dropdown[0]) # TODO EXPAND TO MORE THAN ONE
else:
    print("No include")
    allow_q = None
# 3. exclude dropdown
if exclude_dropdown:
    print("EXCLUDE (TEMP LOCKED TO FIRST FOR DEBUG)")
    restict_q = whoosh.query.Term("source", exclude_dropdown[0]) # TODO EXPAND TO MORE THAN ONE
else:
    print("No exclude")
    restict_q = None
# Age slider

#time slider
'''
Scenarios to setup in order:
1. Get documents for study view
2. Get documents for table view
3. Get variables for metadata view by page.

1.
'''
############ 1
print("\n1")
if len(s) == 0 and not allow_q and not restict_q: # TODO and other terms
    print("1, no extras" )
    qp = qparser.QueryParser("all", ix_spine.schema)
    q = qp.parse("1")
else:
    print("1, with extras" )
    qp = qparser.MultifieldParser(["source", "LPS_name", "table", "table_name", "long_desc", "topic_tags", "Aims", "Themes"], ix_spine.schema, group=qparser.OrGroup)
    q = qp.parse(s)

time0 = time.time()
results = searcher_spine.search(q, filter = allow_q, mask = restict_q, collapse = "source", collapse_limit = 1, limit = 1000)
print(len(results))
l =[]
for hit in results:
    print(hit.keys())
    l.append({key: hit[key] for key in ["source", "Aims"]})
print("Search duration: {}".format(time.time()- time0))
for l1 in l:
    print(l1["source"]) 


########### 2
print("\n2")
if len(s) == 0 and not allow_q and not restict_q: # TODO and other terms
    print("2, no extras" )
    qp = qparser.QueryParser("all", ix_spine.schema)
    q = qp.parse("1")
else:
    print("2, with extras" )

    qp = qparser.MultifieldParser(["source", "LPS_name", "table", "table_name", "long_desc", "topic_tags", "Aims", "Themes"], ix_spine.schema, group=qparser.OrGroup)
    q = qp.parse(s)

time0 = time.time()
results = searcher_spine.search(q, filter = allow_q, mask = restict_q, collapse = "table", limit = 1000)
print(len(results))
l = []
for hit in results:
    l.append({key: hit[key] for key in ["source", "table", "Aims"]})
print("Search duration: {}".format(time.time()- time0))
#for l1 in l:
#    print(l1["source"], l1["table"]) 


########## 3

print("\n3")
time0 = time.time()

if len(s) == 0 and not allow_q and not restict_q: # TODO and other terms
    print("all")
    qp = qparser.QueryParser("all", ix_var.schema)
    q = qp.parse("1")
else:
    print("select")
    qp = qparser.MultifieldParser(["source", "table", "variable_name", "variable_description", "value", "value_label", "topic_tags"], ix_var.schema, group=qparser.OrGroup)
    q = qp.parse(s)
results = searcher_var.search(q, filter = allow_q, mask = restict_q)

l = []
for hit in results:
    l.append({key: hit[key] for key in ["source", "table", "variable_name", "variable_description", "value", "value_label"]})
print(len(l))
print("Search duration: {}".format(time.time()- time0))


'''
searching and collapsing takes about .45 seconds for source and dataset level. Thats probably noticable. 
We will have to do this a lot for study lists, sidebar and dataset view.
Is it worth having a duplicate schema with just dataset level info (no variable level)?
Probably. Lets try it.
NOTE: TODO after a break - do above.
'''

'''
I give up, we can come back to optimising search. For now I will limits returns to 1000 items. upped to 10,000 at a push.
limit does literally nothing...
maybe .3s is acceptable... sod it, we only do it if they are on variable search anyway.'''