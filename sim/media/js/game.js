gCurrentChoice = 0
gFinalSubmit = false

function debug(string)
{
   if (true)
      log("DEBUG " + string)
}

function toggleCharacterProfile(control, characterName)
{
   debug("toggle: " + characterName)
   
   desc = $(characterName + "_description")
   img = $(characterName + "_image")
      
   toggle(desc, 'blind')
   // nit: have to add the overflow style back for text field. it stays set as 'hidden'
   setStyle(desc, {'overflow': 'auto'})
      
   toggle(img, 'slide')
      
   if ('none' == getStyle(desc, 'display'))
      control.innerHTML = 'Character<br />Image'
   else
      control.innerHTML = 'Character<br />Profile'
}

function clearChoice(control)
{
   debug("choose")
   effect = 'blind'
   
   // hide the other choices, leaving the one the user chose
   elements = getElementsByTagAndClassName(null, "player_choice")
   forEach(elements,
           function(elem) 
           {
               if (elem.id != gCurrentChoice && 'none' == getStyle(elem, 'display'))
                  toggle(elem, effect)
           }); 
   
   // hide the feedback form underneath
   toggle($('reasoning_form'), effect)
}

function choose(control, choice)
{
   debug("choose")
   gCurrentChoice = choice
   effect = 'blind'
   
   // hide the other choices, leaving the one the user chose
   elements = getElementsByTagAndClassName(null, "player_choice")
   forEach(elements,
           function(elem) 
           {
               if (elem.id != choice)
                  toggle(elem, effect)
           });   
      
   // show the feedback form underneath
   toggle($('reasoning_form'), effect)
}

function clearMessages()
{
   setStyle($('successMsg'), {'display': 'none'})
   setStyle($('errorMsg'), {'display': 'none'})
}

function saveChoiceSuccess(response)
{
   debug("chooseSuccess: " + response.status)
   
   doc = JSON.parse(response.responseText, null)
   if (doc.result)
   {
      $('successMsg').innerHTML = "Your choices have been saved."
      toggle($('successMsg'), 'blind')
   }
   else
   {
      $('errorMsg').innerHTML = "An error occurred while saving your choices. Please try again."
      toggle($('errorMsg'), 'blind')
   }
}

function saveChoiceError(err)
{
   debug("chooseError: " + err)
   $('errorMsg').innerHTML = err
   toggle($('errorMsg'), 'blind')
}

function saveChoice(control, finalsubmit)
{
   clearMessages()
   
   parts = location.href.split('/')
   groupid = parts[parts.length - 3]
   url = 'http://' + location.hostname + ':' + location.port + "/sim/player/choose/"
   
   deferred = doXHR(url, 
         { 
            method: 'POST', 
            sendContent: queryString({'groupid': groupid, 'choiceid': gCurrentChoice, 'final': finalsubmit, 'reasoning': $('reasoning').value})
         });
   deferred.addCallbacks(saveChoiceSuccess, saveChoiceError);
}

function onLoadSuccess(doc)
{
   
}

function onLoadError(err)
{
   
}

function initializeGame()
{
   clearMessages()
   
   parts = location.href.split('/')
   groupid = parts[parts.length - 3]
   url = 'http://' + location.hostname + ':' + location.port + "/sim/player/status/"
   
   deferred = doXHR(url, 
         { 
            method: 'POST', 
            sendContent: queryString({'groupid': groupid, 'choiceid': gCurrentChoice, 'final': finalsubmit, 'reasoning': $('reasoning').value})
         });
   deferred.addCallbacks(saveChoiceSuccess, saveChoiceError);
}
MochiKit.Signal.connect(window, "onload", initializeGame);
