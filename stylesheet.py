from dash_extensions.javascript import assign

# Dependent layout vars
titlebar_h = 5
left_sidebar_w_perc = "15%"
context_bar_h = 4
sidebar_title_h = 5
body_start = titlebar_h+context_bar_h

####################
# colour palettes ##
####################
peach = ["#EC6552", "#F08475"]
cyan = ["#00ABAA", "#50AFA8"]
lime = ["#CDD500"]
black = ["#000000","#212529", "#373B3E"]
white = ["#FFFFFF", "#F2F2F2", "#E6E6E6", "#212529"]


TITLEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "width": "100%",
    "height": str(titlebar_h)+"rem",
    "background-color": "white",
    "color": "black",
    "textAlign":"center",
    "zIndex":2
    }
#######################


SIDEBAR_LEFT_STYLE = {
    "position": "fixed",
    "top": str(titlebar_h)+"rem",
    "left": 0,
    "bottom": 0,
    "width":left_sidebar_w_perc,
    "min-width":"10rem",
    "zIndex":1,
    }

SIDEBAR_TITLE_STYLE = {
    "background-color":"black",
    "color":"white",
    "height": str(sidebar_title_h)+"rem",
    "border-right" : "solid",
    "border-width":"thin",
    "border-color" : "white",
}

SIDEBAR_LIST_DIV_STYLE = {
    "position":"relative",
    "background-color":"#212529",
    "height": "calc(100% - "+str(sidebar_title_h+5)+"rem",
    "overflow-y": "scroll",
    "overflow-x": "hidden",
}

SIDEBAR_FOOTER_STYLE = {
    "position":"relative",
    "left": 0,
    "height": "5rem",
    "min-width":"10rem",
    "background-color" : "black",
    "color" : "white",
    'textAlign': 'center',
}

SCHEMA_LIST_STYLE = {
    "list-style-type":"none",
    "border-bottom": "solid",
    "border-width":"thin",
    }

SCHEMA_LIST_ITEM_STYLE = {
    "border-top":"solid",
    "border-bottom":"solid",
    "border-width":"thin",
    "font-size":"medium",
    "background-color": "#212529",
    "color":"white",
    }

COLLAPSE_DIV_STYLE = {
    "list-style-type":"none", 
    "border-top":"solid",
    "border-width":"thin",
    "font-size":"small",
    }
TABLE_LIST_STYLE = {
    "border-top":"solid",
    "border-width":"thin",
    }
TABLE_LIST_ITEM_STYLE = {

    "border-bottom":"solid",
    "border-width":"thin",
    "overflow":"hidden",
    "background": "white",

    }

######################################

CONTEXT_BAR_STYLE = {
    "position": "fixed",
    "top": str(titlebar_h)+"rem",
    "height" : str(context_bar_h)+"rem",
    "width":"85%",
    "left":"15%",
    "background-color": "black",
    "overflow-x":"hidden",
    "zIndex":2,
    "border-bottom":"solid",
    "border-width":"thin",
    "border-color":"white"
}

BUTTON_STYLE = {
    "float":"left",
    "margin":"1rem"
}


######################################

BODY_STYLE = {
    "position": "relative",
    "top": str(titlebar_h+context_bar_h)+"rem",
    "left":"15%",
    "width":"85%",
    "height":"calc(100%-"+str(titlebar_h+context_bar_h)+")",
    "zIndex":0,
    "overflow-x":"hidden",
    }

HIDDEN_BODY_STYLE = {
    "display":"none"
}    

# Map #################################

MAP_DIV_STYLE = {
    }

MAP_TITLE_STYLE = {
    "width":"100%",
    "height":"3rem",
    "color":"white",
    "background-color":cyan[0],
    "padding-top":"0.5rem",
    "padding-left":"1rem",
}

DYNA_MAP_STYLE = {
    "height" : "30vw",
}

POLYGON_STYLE = assign("""function(feature, context){
        return weight=5, color='#666', dashArray='';
};""")

# Documentation #######################

DOC_TITLE_STYLE = {
    "width":"100%",
    "height":"3rem",
    "color":"white",
    "background-color":black[0],
    "padding-top":"0.5rem",
    "padding-left":"1rem",
}

DOCUMENTATION_BOX_STYLE ={
    "color":"white",
    "background-color":black[2],

    "padding" : "1rem"
}

TABLE_DOC_DIV = {
}

TABLES_DOC_HEADER = {
    'textAlign': 'left',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'whiteSpace': 'normal',
    'height': 'auto',
    "background-color":black[0],
    "color":"white"
}

TABLES_DOC_CELL = {
    'textAlign': 'left',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'whiteSpace': 'normal',
    'height': 'auto',
    "background-color":black[1],
    }
TABLES_DOC_CONDITIONAL = {'if': {
        'row_index': 'even'
    },
    'backgroundColor': black[2],
}

# METADATA #######################
METADATA_TITLE_STYLE = {
    "width":"100%",
    "height":"3rem",
    "color":"black",
    "background-color":white[0],
    "padding-top":"0.5rem",
    "padding-left":"1rem",
}

METADATA_BOX_STYLE = {
    "color":"white",
    "background-color":white[2],
    "padding" : "1rem"
}

METADATA_DESC_HEADER = {
    'textAlign': 'left','overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'whiteSpace': 'normal',
    'height': 'auto',
    "background-color":white[3],
    "color":"white"
}

METADATA_DESC_CELL = {
    'textAlign': 'left',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'whiteSpace': 'normal',
    'height': 'auto',
    "background-color":white[1],
    "color":"black"
}

METADATA_TABLE_DIV_STYLE = {
    "margin-top" : "1rem",
}

METADATA_TABLE_HEADER = {
    'textAlign': 'left',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'whiteSpace': 'normal',
    'height': 'auto',
    "background-color":white[3],
    "color":"white"
}

METADATA_TABLE_CELL = {
    'textAlign': 'left',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'whiteSpace': 'normal',
    'height': 'auto',
    "background-color":white[1],
    "color":"black"
    }

METADATA_CONDITIONAL = {'if': {
        'row_index': 'even'
    },
    'backgroundColor': white[2]
}

###################################
APP_STYLE = {
    "height":"100vh",
    "width": "100wh",

}