from dash_extensions.javascript import assign

# Dependent layout vars
titlebar_h = 5
left_sidebar_w_perc = "15%"
context_bar_height = 2

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
SIDEBAR_LEFT_STYLE = {
    "background":"black",
    "position": "fixed",
    "top": "5rem",
    "left": 0,
    "bottom": 0,
    "width":left_sidebar_w_perc,
    "min-width":"10rem",
    "zIndex":1,
    "border-right":"solid",
    "border-width":"normal",
    "color":"white",
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
    "border-width":"thin",
    "font-size":"medium",
    "background-color": "#212529",
    "color":"white"
    }

COLLAPSE_DIV_STYLE = {
    "list-style-type":"none", 
    "border-top":"solid",
    "border-width":"thin",
    "font-size":"small"
    }
TABLE_LIST_STYLE = {
    "border-top":"solid",
    "border-width":"thin",
    }
TABLE_LIST_ITEM_STYLE = {
    "border-bottom":"solid",
    "border-width":"thin",
    "overflow":"hidden",
    "background": "white"
    }

######################################

CONTEXT_BAR_STYLE = {
    "top": str(titlebar_h)+"rem",
    "height" : str(context_bar_height)+"rem",
    "border-width":"thin",
    "border-color":"black",
    "left":"15%",
    "width":"85%",
    "background-color": "black",
    "width":"20rem",
    "border":"solid",
}



######################################

BODY_STYLE = {
    "position": "relative",
    "top": str(titlebar_h+context_bar_height)+"rem",
    "left":"15%",
    "width":"85%",
    "height":"100%",
    
    "zIndex":0,
    "overflow-y":"scroll",
    "overflow-x":"hidden",
    }

DYNA_MAP_STYLE = {
    "height" : "40vw"

}

POLYGON_STYLE = assign("""function(feature, context){
        return weight=5, color='#666', dashArray='';
};""")