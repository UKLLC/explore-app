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
    "border-color" : "white",

}

SIDEBAR_LIST_DIV_STYLE = {
    "position":"relative",
    "background-color":"#212529",
    "height": "calc(100% - "+str(sidebar_title_h)+"rem",
    "overflow-y": "scroll",
    "overflow-x": "hidden",
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
    "position": "relative",
    "top": str(titlebar_h)+"rem",
    "height" : str(context_bar_h)+"rem",
    "width":"85%",
    "left":"15%",
    "background-color": "black",
    "overflow-x":"hidden",
}


######################################

BODY_STYLE = {
    "position": "relative",
    "top": str(titlebar_h)+"rem",
    "left":"15%",
    "width":"85%",
    "height":"100%",
    "zIndex":0,
    "overflow-y":"scroll",
    "overflow-x":"hidden",

    "border" : "solid",
    "border-color" : "green",
    }

MAP_DIV_STYLE = {
    "width":"100%",
    "height":"100%",

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

###################################
APP_STYLE = {
    "height":"100vh",
    "width": "100wh",

}