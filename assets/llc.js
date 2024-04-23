// This default onbeforeunload event
window.onbeforeunload = function(){
    return "Do you want to leave?"
}

document.addEventListener("onbeforeunload", function() 
{   
    document.getElementById('hiddenButton').dispatchEvent(new Event(click))})