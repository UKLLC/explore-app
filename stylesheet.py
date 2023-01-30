from turtle import position
from dash_extensions.javascript import assign

# Dependent layout vars
titlebar_h = 5
left_sidebar_w = 16
context_bar_h = 4
sidebar_title_h = 5
body_start = titlebar_h+context_bar_h
box_title_h = 3
box_content_start = body_start + box_title_h


####################
# colour palettes ##
####################
peach = ["#EC6552", "#F08475"]
cyan = ["#00ABAA", "#50AFA8"]
lime = ["#CDD500"]
black = ["#000000","#212529", "#373B3E", "#1c1c1c"]
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
    "zIndex":2,
    }


LOGOS_STYLE = {
    "height" : str(titlebar_h)+"rem",
    "left" : 0,
    "margin-right" : "1rem"
}

LOGOS_DIV_STYLE = {
    "position" : "fixed",
    "left" : 0,
    "align": "left",

    "width":"15%"
}
#######################


SIDEBAR_LEFT_STYLE = {
    "position" : "fixed",
    "top" : str(titlebar_h)+"rem",
    "left" : 0,
    "bottom": 0,
    "width" : str(left_sidebar_w)+"rem",
    "zIndex" : 1,
    }

SIDEBAR_TITLE_STYLE = {
    "background-color":black[3],
    "color":"white",
    "height": str(sidebar_title_h)+"rem",

    "border-bottom" : "solid",
    "border-width" : "thin",

    "border-color" : "white",
    "padding-left" : ".5rem",
    "padding-top" : ".5rem",
}


SIDEBAR_LIST_DIV_STYLE = {
    "zIndex":3,
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
    "background-color" : black[3],
    "color" : "white",
    'textAlign': 'center',
    "border-top" : "solid",
    "border-width" : "thin",
    "border-color" : "white",    
}

###############



# checkbox and tables combined
CHECKBOX_LIST_COLS_STYLE = {
    "list-style-type":"none", 
    "border-top":"solid",
    "border-width":"thin",
    "font-size":"small",
    "width" : "100%",
    "display" : "flex",
    "width" : "16rem",
    "color" : "black",
}


# checkbox column
CHECKBOX_COL_STYLE = {
    "zIndex":2,
    "width":"2rem",

    "border" : "none"
}

#checkbox row
CHECKBOX_ROW_STYLE = {
    "width":"1rem",
    "height" : "2rem",

    #"border-bottom":"solid",
    #"border-width":"thin",
    #"border-color":"black",
    "border" : "none",
    "background-color": "none",
    'align-items': 'center',
    'justify-content': 'center',
    "padding":".4rem"
}

CHECKBOX_STYLE = {
    "content" : "none",
    "width" : "2rem",
    "font-size":"0"
}

######################################

CONTEXT_BAR_STYLE = {
    "position": "fixed",
    "top": str(titlebar_h)+"rem",
    "height" : str(context_bar_h)+"rem",
    "width":"calc(100% - "+str(left_sidebar_w)+"rem)",
    "left":str(left_sidebar_w)+"rem",
    "background-color": "white",
    "overflow-x":"hidden",
    "zIndex":2,
    "border-bottom":"solid",
    "border-width":"thin",
    "border-color":"white"
}



######################################

BODY_STYLE = {
    "position": "fixed",
    "top": str(titlebar_h+context_bar_h)+"rem",
    "left":str(left_sidebar_w)+"rem",
    "width":"calc(100% - "+str(left_sidebar_w)+"rem)",
    "height":"calc(100% - "+str(body_start)+"rem)",
    "zIndex":0,
    "overflow":"hidden",
    }

HIDDEN_BODY_STYLE = {
    "display":"none"
}    

BOX_STYLE = {
    "height" : "100%",
}

# Map #################################

MAP_TITLE_STYLE = {
    "width":"100%",
    "height":"3rem",
    "color":"white",
    "background-color":cyan[0],
    "padding-top":"0.5rem",
    "padding-left":"1rem",
}

MAP_BOX_STYLE = {
    "height" : "100%",
    "top" : str(box_title_h) +"rem",
    "height":"calc(100% - "+str(box_title_h) +"rem)",
}
DYNA_MAP_STYLE = {
    "height" : "100%",
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
    "padding" : "1rem",
    "padding-bottom" : "1rem",
    "top" : str(box_title_h) +"rem",
    "height":"calc(100% - "+str(box_title_h) +"rem)",
    "overflow-y":"scroll",
    "line-height": "1.6"
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
    "background-color":white[2],
    "padding" : "1rem",
    "top" : str(box_title_h) +"rem",
    "height":"calc(100% - "+str(box_title_h) +"rem)",
    "overflow-y":"scroll",
    "color":"black"
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

LANDING_TITLE_STYLE = {
    "width":"100%",
    "height":"3rem",
    "color":"black",
    "background-color":white[0],
    "padding-top":"0.5rem",
    "padding-left":"1rem",
}

LANDING_BOX_STYLE = {
    "color":"black",
    "background-color":white[0],
    "padding" : "1rem",
    "height" : "100%"
}

###################################
APP_STYLE = {
    "height":"100vh",
    "width": "100wh",

}