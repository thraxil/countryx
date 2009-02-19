function clearMessages()
{
   elements = getElementsByTagAndClassName(null, "error")
   forEach(elements,
           function(elem) 
           {
              setStyle(elem, {'display': 'none'})
           });   
   
   elements = getElementsByTagAndClassName(null, "success")
   forEach(elements,
           function(elem) 
           {
              setStyle(elem, {'display': 'none'})
           }); 
}

function submitFeedback(form, player_id)
{
   alert("submitFeedback")
   clearMessages()
   
   if (form.feedback.value.length < 1)
   {
      id = 'error_client_' + form.turn_id.value
      $(id).innerHTML = "Please enter some feedback before submitting."
      setStyle($(id), {'display': 'block'})
   }
   else
   {
      url = 'http://' + location.hostname + ':' + location.port + "/sim/faculty/feedback/"
      
      deferred = doXHR(url, 
            { 
               method: 'POST', 
               sendContent: queryString({'player_id': player_id, 'turn_id': form.turn_id.value, 'feedback': form.feedback.value, 'faculty_id': form.faculty_id.value})
            });
      deferred.addCallbacks(submitFeedbackSuccess, submitFeedbackError);
   }
   
   return false;
}

function submitFeedbackSuccess(response)
{
   doc = JSON.parse(response.responseText, null)
   if (doc.result == 0)
   {
      id = 'error_client_' + doc.turn_id
      $(id).innerHTML = doc.message
      setStyle($(id), {'display': 'block'})
   }
   else if (doc.result == 1)
   {
      id = 'success_client_' + doc.turn_id
      $(id).innerHTML = doc.message
      setStyle($(id), {'display': 'block'})
   }
}

function submitFeedbackError(err)
{
   alert(err)
}