gCurrentChoice = 0

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
   clearMessages()
   gCurrentChoice = 0
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
   if (gCurrentChoice == 0)
   {
      debug("choose: " + gCurrentChoice + " >> " + choice)
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
}

function clearMessages()
{
   setStyle($('successMsg'), {'display': 'none'})
   setStyle($('errorMsg'), {'display': 'none'})
   setStyle($('errorClient'), {'display': 'none'})
}

function saveChoiceSuccess(response)
{
   debug("chooseSuccess: " + response.status)
   
   doc = JSON.parse(response.responseText, null)
   if (doc.result == 0)
   {
      $('errorMsg').innerHTML = "An error occurred while saving your choices. Please try again."
      toggle($('errorMsg'), 'blind')
   }
   else if (doc.result == 1)
   {
      // draft -- leave the screen the way it was
      $('successMsg').innerHTML = "Your choices have been saved."
      toggle($('successMsg'), 'blind')
      $('submit_state_desc').innerHTML = "Decision Pending"
   }
   else if (doc.result == 2)
   {
      // submit succeeded -- hide the selection divs

      // submit -- leave the screen the way it was
      $('successMsg').innerHTML = "Your choices have been submitted."
      toggle($('successMsg'), 'blind')
      
      $(gCurrentChoice).onclick = ''
      setNodeAttribute($('reasoning'), 'readonly', 'true')
      setStyle($('savedraft'), {'display': 'none'})
      setStyle($('submit'), {'display': 'none'})
      setStyle($('clear'), {'display': 'none'})
      $('submit_state_desc').innerHTML = "Final Submission"
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
   
   if (finalsubmit && $('reasoning').value.length < 1)
   {
      $('errorClient').innerHTML = "Please enter your reasoning before submitting a final answer."
      toggle($('errorClient'), 'blind')
   }
   else if (finalsubmit && !confirm("Are you sure you're ready to submit your choice and reasoning? Your responses are final once you hit OK"))
   {
      return // do nothing
   }
   else if (gCurrentChoice == 0)
   {
      alert("Current Choice is 0?")
   }
   else
   {
      parts = location.href.split('/')
      groupid = parts[parts.length - 2]
      url = 'http://' + location.hostname + ':' + location.port + "/sim/player/choose/"
      
      debug("group id: " + groupid)
      
      deferred = doXHR(url, 
            { 
               method: 'POST', 
               sendContent: queryString({'groupid': groupid, 'choiceid': gCurrentChoice, 'final': finalsubmit, 'reasoning': $('reasoning').value})
            });
      deferred.addCallbacks(saveChoiceSuccess, saveChoiceError);
   }
}

function initializeGame()
{
   gCurrentChoice = $('current_choice').innerHTML
}
MochiKit.Signal.connect(window, "onload", initializeGame);